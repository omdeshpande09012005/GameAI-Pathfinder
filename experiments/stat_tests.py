#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

EVAL = Path("results") / "eval_runs.csv"
OUT = Path("results") / "stat_tests.txt"

def main():
    if not EVAL.exists():
        print("[error] missing eval_runs.csv; cannot run statistical tests")
        return
    df = pd.read_csv(EVAL)
    if 'method' not in df.columns or 'steps' not in df.columns:
        print("[error] eval_runs.csv lacks required columns 'method' or 'steps'")
        return
    # pair by map and run if possible
    if 'map_name' in df.columns and 'run' in df.columns:
        pivot = df.pivot_table(index=['map_name','run'], columns='method', values='steps', aggfunc='mean')
        # keep rows where both methods present
        pivot = pivot.dropna()
        if pivot.shape[0] == 0:
            print("[error] no paired rows found in eval_runs.csv")
            return
        # assume columns include 'A*' and some Q label; pick first A* and first Q-like
        cols = list(pivot.columns)
        a_col = next((c for c in cols if 'A*' in str(c) or 'astar' in str(c).lower()), None)
        q_col = next((c for c in cols if 'Q' in str(c) or 'qlearn' in str(c).lower() or 'q-learning' in str(c).lower()), None)
        if a_col is None or q_col is None:
            # fallback: take first two columns and assume A* is one and Q-Learning the other
            a_col, q_col = cols[0], cols[1] if len(cols) > 1 else (cols[0], None)
        a = pivot[a_col].values
        q = pivot[q_col].values if q_col is not None else None
    else:
        # fallback: try to find method names and pair by run only
        methods = df['method'].unique()
        if len(methods) < 2:
            print("[error] need at least two methods in eval_runs.csv")
            return
        methods = list(methods)
        m1, m2 = methods[0], methods[1]
        df1 = df[df['method']==m1].sort_values('run')
        df2 = df[df['method']==m2].sort_values('run')
        merged = pd.merge(df1, df2, on='run', suffixes=('_1','_2'))
        a = merged['steps_1'].values
        q = merged['steps_2'].values
    # stat tests
    dif = a - q
    out = []
    out.append(f"N paired: {len(dif)}")
    if len(dif) >= 3:
        sh = stats.shapiro(dif)
        out.append(f"Shapiro-Wilk on differences: W={sh.statistic:.4f}, p={sh.pvalue:.4e}")
        normal = sh.pvalue > 0.05
    else:
        out.append("Too few samples for Shapiro-Wilk; using non-parametric test by default")
        normal = False
    if normal:
        t = stats.ttest_rel(a,q)
        out.append(f"Paired t-test: t={t.statistic:.4f}, p={t.pvalue:.4e}")
    else:
        try:
            w = stats.wilcoxon(a,q)
            out.append(f"Wilcoxon signed-rank: W={w.statistic:.4f}, p={w.pvalue:.4e}")
        except Exception as e:
            out.append("Wilcoxon failed: " + str(e))
    # effect size (paired Cohen's d)
    es = (np.mean(dif)) / (np.std(dif, ddof=1) if np.std(dif, ddof=1) > 0 else np.nan)
    out.append(f"Cohen's d (paired): {es:.4f}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write("\n".join(out))
    print("[ok] wrote stats report to", OUT)
    for line in out: print(line)

if __name__ == "__main__":
    main()
