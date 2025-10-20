#!/usr/bin/env python3
"""
analyze.py

Robust analyzer for GameAI-Pathfinder.

Behavior summary:
 - Looks for per-episode training CSVs named like qlearning_train_<N>.csv and plots learning curves.
 - Attempts to find or build an `results/eval_runs.csv` by scanning results/ for eval files.
 - Produces aggregated summary CSV results/table_summary.csv and the PNG plots used by the LaTeX paper.
 - Is tolerant to different column names (will try to auto-detect 'episode' and 'reward', or fallback).
"""
import os, glob, re, sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

RESULTS_DIR = Path("results")
PLOTS_DIR = RESULTS_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

QL_PATTERN = RESULTS_DIR / "qlearning_train_*.csv"
EVAL_MASTER = RESULTS_DIR / "eval_runs.csv"
SUMMARY_OUT = RESULTS_DIR / "table_summary.csv"
MA_WINDOW = 25

def safe_read_csv(p: Path):
    try:
        return pd.read_csv(p)
    except Exception as e:
        print(f"[warn] failed to read {p}: {e}")
        return None

def find_reward_col(df):
    # heuristics to find 'reward' column
    candidates = [c for c in df.columns if 'reward' in c.lower() or 'rew' in c.lower()]
    if candidates:
        return candidates[0]
    # fallback numeric column with many distinct values
    numerics = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if numerics:
        # pick the numeric column with highest variance (likely reward)
        varcols = sorted(numerics, key=lambda c: df[c].var() if df[c].dtype.kind in 'fi' else -1, reverse=True)
        return varcols[0]
    return None

def find_episode_col(df):
    candidates = [c for c in df.columns if 'episode' in c.lower() or 'ep' == c.lower()]
    if candidates:
        return candidates[0]
    # fallback: if index-like column exists with incremental ints
    for c in df.columns:
        if pd.api.types.is_integer_dtype(df[c]) or pd.api.types.is_float_dtype(df[c]):
            vals = df[c].dropna().astype(int).values
            if len(vals) > 1 and np.all(np.diff(vals) >= 0):
                return c
    return None

def moving_average(x, w):
    if w <= 1 or len(x) == 0:
        return np.array(x)
    return np.convolve(x, np.ones(w)/w, mode='valid')

def plot_learning_curves():
    files = sorted(RESULTS_DIR.glob("qlearning_train_*.csv"))
    if not files:
        print("[info] no qlearning_train_*.csv files found.")
        return
    for f in files:
        df = safe_read_csv(f)
        if df is None:
            continue
        reward_col = find_reward_col(df)
        ep_col = find_episode_col(df)
        if reward_col is None:
            print(f"[warn] {f.name} missing reward-like column; skipping.")
            continue
        rewards = df[reward_col].values
        if ep_col is not None:
            episodes = df[ep_col].values
        else:
            episodes = np.arange(len(rewards))
        ma = moving_average(rewards, MA_WINDOW)
        x_raw = episodes
        x_ma = episodes[(len(episodes)-len(ma))//2 : (len(episodes)-len(ma))//2 + len(ma)] if len(ma)>0 else episodes
        plt.figure(figsize=(6.4,3.3))
        plt.plot(x_raw, rewards, linewidth=0.6, label='raw')
        if len(ma)>0:
            plt.plot(x_ma, ma, linewidth=1.2, label=f'ma({MA_WINDOW})')
            std = pd.Series(rewards).rolling(window=MA_WINDOW, min_periods=1).std().values
            std_ma = std[MA_WINDOW-1:]
            if len(std_ma) == len(ma):
                plt.fill_between(x_ma, ma - std_ma, ma + std_ma, alpha=0.12)
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title(f"Learning curve ({f.stem})")
        plt.legend()
        out = PLOTS_DIR / f"learning_curve_{f.stem.split('_')[-1]}.png"
        plt.tight_layout()
        plt.savefig(out, dpi=150)
        plt.close()
        print("[ok] wrote", out)

# --- eval aggregator: try to build eval_runs.csv if missing --- #
def auto_build_eval_master():
    if EVAL_MASTER.exists():
        print("[info] found existing", EVAL_MASTER)
        return True
    # look for plausible eval files: names like eval_*.csv or *_eval.csv or results_*_eval.csv or per-config files
    candidates = list(RESULTS_DIR.glob("*eval*.csv")) + list(RESULTS_DIR.glob("eval_*.csv")) + list(RESULTS_DIR.glob("eval-*.csv"))
    # also include files named like results_eval_<config>.csv or *_posteval.csv
    candidates = sorted(set(candidates))
    if not candidates:
        print("[info] no per-config eval CSVs found to aggregate.")
        return False
    rows = []
    for p in candidates:
        df = safe_read_csv(p)
        if df is None: 
            continue
        # heuristic to identify columns: method, run, steps, success, map_name
        cols = {c.lower():c for c in df.columns}
        method_col = cols.get('method') or cols.get('algo') or cols.get('algorithm') or None
        run_col = cols.get('run') or cols.get('trial') or None
        steps_col = cols.get('steps') or cols.get('step') or cols.get('length') or None
        succ_col = cols.get('success') or cols.get('succ') or cols.get('solved') or None
        map_col  = cols.get('map') or cols.get('map_name') or cols.get('env') or None
        # if file contains method implicitly (e.g., filename contains "astar" or "qlearning"), set method column
        fname = p.stem.lower()
        implicit_method = None
        if 'astar' in fname: implicit_method = "A*"
        if 'qlearn' in fname or 'q-learning' in fname or 'qlearning' in fname: implicit_method = "Q-Learning"
        # build rows
        for idx, r in df.iterrows():
            row = {}
            row['method'] = r[method_col] if method_col else implicit_method if implicit_method else "unknown"
            row['config'] = r.get('config', p.stem) if 'config' in df.columns else p.stem
            row['run'] = int(r[run_col]) if run_col and pd.notna(r[run_col]) else int(idx)
            if steps_col and pd.notna(r[steps_col]): 
                row['steps'] = float(r[steps_col])
            else:
                # maybe there is 'steps_to_goal' or 'steps_taken'
                matched = None
                for tryc in ['steps_to_goal','steps_taken','nsteps','episodes','length']:
                    if tryc in df.columns:
                        matched = tryc; break
                row['steps'] = float(r[matched]) if matched and pd.notna(r[matched]) else np.nan
            if succ_col and pd.notna(r[succ_col]):
                row['success'] = int(bool(r[succ_col]))
            else:
                # infer success from steps not nan and maybe steps < max_steps
                row['success'] = int(not np.isnan(row['steps']))
            row['map_name'] = r[map_col] if map_col and pd.notna(r[map_col]) else p.stem
            rows.append(row)
    if not rows:
        print("[info] aggregator found no usable rows.")
        return False
    outdf = pd.DataFrame(rows)
    outdf.to_csv(EVAL_MASTER, index=False)
    print("[ok] created aggregated eval CSV:", EVAL_MASTER)
    return True

def build_summary_and_plots():
    if not EVAL_MASTER.exists():
        print("[warn] no eval_runs.csv found; skipping eval aggregation/plots.")
        return None, None
    df = safe_read_csv(EVAL_MASTER)
    if df is None:
        return None, None
    # coerce numeric columns where possible
    if 'steps' in df.columns:
        df['steps'] = pd.to_numeric(df['steps'], errors='coerce')
    if 'success' in df.columns:
        df['success'] = pd.to_numeric(df['success'], errors='coerce').fillna(0).astype(int)
    # compute group summary
    grp = df.groupby(['method','config']).agg(
        runs = ('run','nunique'),
        success_rate = ('success','mean'),
        mean_steps = ('steps','mean'),
        std_steps = ('steps','std')
    ).reset_index()
    if not grp.empty:
        grp['success_pct'] = (grp['success_rate']*100).round(2)
        out = grp[['method','config','runs','success_pct','mean_steps','std_steps']]
        out.to_csv(SUMMARY_OUT, index=False)
        print("[ok] wrote aggregated summary:", SUMMARY_OUT)
    # produce plots if enough data
    try:
        # success rate vs training episodes (if 'train' in config)
        df2 = df.copy()
        def extract_train(cfg):
            if pd.isna(cfg): return np.nan
            m = re.search(r'train[_=]?(\d{2,5})', str(cfg))
            if m: return int(m.group(1))
            r = re.search(r'(\d{3,5})', str(cfg))
            return int(r.group(1)) if r else np.nan
        df2['train_episodes'] = df2['config'].apply(extract_train)
        ql = df2[df2['method'].str.contains('Q', na=False)]
        if not ql.empty and ql['train_episodes'].notna().any():
            sr = ql.groupby('train_episodes').agg(success_rate=('success','mean')).reset_index()
            plt.figure(figsize=(5.5,3.0))
            plt.plot(sr['train_episodes'], sr['success_rate']*100, marker='o')
            plt.xlabel('Training episodes'); plt.ylabel('Success rate (%)')
            plt.title('Success rate vs training episodes (Q-Learning)')
            plt.grid(axis='y', alpha=0.2)
            plt.tight_layout(); plt.savefig(PLOTS_DIR / 'success_rate_vs_train.png', dpi=150); plt.close()
            print("[ok] wrote", PLOTS_DIR / 'success_rate_vs_train.png')
        # success bar per method
        sb = df.groupby('method').agg(success_rate=('success','mean')).reset_index()
        plt.figure(figsize=(4.8,3.2))
        plt.bar(sb['method'], sb['success_rate']*100)
        plt.ylabel('Success rate (%)'); plt.title('Success rate by method')
        plt.tight_layout(); plt.savefig(PLOTS_DIR / 'success_rate.png', dpi=150); plt.close()
        print("[ok] wrote", PLOTS_DIR / 'success_rate.png')
        # path length comparison boxplot
        try:
            import seaborn as sns
            plt.figure(figsize=(5.5,3.2))
            sns.boxplot(x='method', y='steps', data=df)
            plt.ylabel('Steps to goal'); plt.title('Path length comparison')
            plt.tight_layout(); plt.savefig(PLOTS_DIR / 'path_length_comparison.png', dpi=150); plt.close()
            print("[ok] wrote", PLOTS_DIR / 'path_length_comparison.png')
        except Exception:
            groups = [g['steps'].dropna().values for _, g in df.groupby('method')]
            labels = [m for m,_ in df.groupby('method')]
            plt.figure(figsize=(5.5,3.2))
            plt.boxplot(groups, labels=labels, patch_artist=True)
            plt.ylabel('Steps'); plt.title('Path length comparison')
            plt.tight_layout(); plt.savefig(PLOTS_DIR / 'path_length_comparison.png', dpi=150); plt.close()
            print("[ok] wrote (fallback)", PLOTS_DIR / 'path_length_comparison.png')
        # steps per run pivot
        try:
            pivot = df.pivot_table(index='run', columns='method', values='steps', aggfunc='mean')
            if not pivot.empty:
                ax = pivot.plot(kind='bar', figsize=(6.0,3.2))
                ax.set_ylabel("Steps"); ax.set_title("Steps per evaluation run")
                plt.tight_layout(); plt.savefig(PLOTS_DIR / 'steps_per_run.png', dpi=150); plt.close()
                print("[ok] wrote", PLOTS_DIR / 'steps_per_run.png')
        except Exception:
            pass
    except Exception as e:
        print("[warn] plotting failed:", e)
    return df, None

def main():
    print("[run] analyze.py")
    plot_learning_curves()
    built = auto_build_eval_master()
    if not built:
        print("[info] no evaluation data available to aggregate -> summary plots skipped.")
    df, _ = build_summary_and_plots()
    print("[done] analysis complete. Check", PLOTS_DIR, "and", SUMMARY_OUT)

if __name__ == "__main__":
    main()
