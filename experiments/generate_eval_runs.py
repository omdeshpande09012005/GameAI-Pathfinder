#!/usr/bin/env python3
"""
generate_eval_runs.py

Tries to extract evaluation rows from existing qlearning CSVs, otherwise synthesizes
a conservative eval_runs.csv from table_summary_fixed.csv.

Outputs: results/eval_runs.csv with columns:
    method,config,run,steps,success,map_name

Run from repository root:
    python experiments/generate_eval_runs.py
"""

import pandas as pd
from pathlib import Path
import numpy as np
import re

ROOT = Path(".")
RESULTS = ROOT / "results"
PATTERN = re.compile(r"qlearning_train.*\.csv")

RESULT_FILE = RESULTS / "eval_runs.csv"
TABLE_SUMMARY = RESULTS / "table_summary_fixed.csv"

def scan_qlearning_files():
    candidates = sorted([p for p in RESULTS.iterdir() if PATTERN.match(p.name)])
    rows = []
    for p in candidates:
        try:
            df = pd.read_csv(p)
        except Exception as e:
            print(f"[warn] failed to read {p.name}: {e}")
            continue
        # possible column name sets that could encode eval rows
        # we'll look for any rows flagged as eval, or columns that look like 'eval_steps' or 'eval_success'
        eval_rows = pd.DataFrame()
        # If there is a 'phase' or 'mode' column that marks 'eval' rows:
        if 'phase' in df.columns:
            eval_rows = df[df['phase'].astype(str).str.lower().isin(['eval','evaluation','test'])]
        if eval_rows.empty and 'mode' in df.columns:
            eval_rows = df[df['mode'].astype(str).str.lower().isin(['eval','test','evaluation'])]
        # common names:
        possible_pairs = [
            ('eval_steps','eval_success'),
            ('eval_steps','success'),
            ('steps','success'),
            ('steps','eval_success'),
            ('steps','eval'),
            ('eval','success'),
            ('eval_steps','success_flag'),
            ('eval_steps','success_bool'),
        ]
        if eval_rows.empty:
            for a,b in possible_pairs:
                if a in df.columns and b in df.columns:
                    eval_rows = df[[a,b]].copy()
                    eval_rows.columns = ['steps','success']
                    break
        # sometimes there is one row at the end with aggregated eval columns:
        if eval_rows.empty:
            # search any column names for 'eval' and 'step' / 'success' patterns
            cols = df.columns.str.lower()
            step_cols = [c for c in df.columns if re.search(r"step", c, re.I)]
            succ_cols = [c for c in df.columns if re.search(r"succ|success|win|solved", c, re.I)]
            if step_cols and succ_cols:
                # pick last row(s)
                eval_rows = df.loc[df.index[-1:], step_cols + succ_cols]
                # rename first two to steps/success (best-effort)
                use_step = step_cols[0]
                use_succ = succ_cols[0]
                eval_rows = eval_rows[[use_step, use_succ]].copy()
                eval_rows.columns = ['steps','success']
        # if still empty, skip
        if eval_rows.empty:
            print(f"[info] {p.name}: no eval rows found (tried common column names).")
            continue
        # normalize rows to expected format
        for idx, r in eval_rows.iterrows():
            try:
                steps = int(r['steps'])
            except Exception:
                try:
                    steps = int(float(r['steps']))
                except:
                    steps = 10000
            succ_raw = r['success']
            success = 1 if str(succ_raw).strip().lower() in ['1','true','yes','win','solved','success'] or float(succ_raw) > 0.5 else 0
            method = "qlearning"
            config = p.stem
            runnum = int(idx) if isinstance(idx, (int, np.integer)) else 1
            rows.append({
                "method": method,
                "config": config,
                "run": runnum,
                "steps": steps,
                "success": success,
                "map_name": p.stem
            })
    return rows

def synthesize_from_table():
    if not TABLE_SUMMARY.exists():
        print(f"[error] summary not found: {TABLE_SUMMARY}")
        return []
    df = pd.read_csv(TABLE_SUMMARY)
    # expected columns: train_episodes / algo / runs / success_rate / avg_steps / std_steps / avg_time_ms
    rows = []
    for _, r in df.iterrows():
        method = r.get('algo') or r.get('method') or r.get('config') or 'qlearning'
        # try fields
        succ_pct = r.get('success_rate') or r.get('success_pct') or r.get('success')
        try:
            succ_pct = float(succ_pct)
        except:
            succ_pct = np.nan
        mean = r.get('avg_steps') or r.get('mean_steps') or r.get('mean') or 10000.0
        std = r.get('std_steps') or r.get('std') or 1.0
        try:
            mean = float(mean)
        except:
            mean = 10000.0
        try:
            std = float(std)
        except:
            std = max(1.0, 0.05 * abs(mean))
        runs = int(r.get('runs') or 3)
        for run in range(1, runs+1):
            # sample steps from normal, clamp to sensible integers
            sampled = int(max(1, np.round(np.random.normal(loc=mean, scale=max(std,1.0)))))
            success = 1 if (not np.isnan(succ_pct) and succ_pct >= 50.0) else 0
            rows.append({
                "method": method,
                "config": f"{method}_synth",
                "run": run,
                "steps": sampled,
                "success": success,
                "map_name": "synth_map"
            })
    return rows

def main():
    RESULTS.mkdir(exist_ok=True)
    rows = scan_qlearning_files()
    if rows:
        print(f"[ok] extracted {len(rows)} eval rows from qlearning files.")
    else:
        print("[warn] no eval rows found in qlearning CSVs; attempting to synthesize from table_summary_fixed.csv")
        rows = synthesize_from_table()
        if rows:
            print(f"[ok] synthesized {len(rows)} eval rows from table_summary_fixed.csv for pipeline testing.")
        else:
            print("[error] nothing to write — please run the evaluation step that generates per-run eval rows or ensure table_summary_fixed.csv exists.")
            return 1
    outdf = pd.DataFrame(rows)
    # enforce expected column order
    outdf = outdf[['method','config','run','steps','success','map_name']]
    outdf.to_csv(RESULT_FILE, index=False)
    print("[ok] wrote:", RESULT_FILE, "rows:", len(outdf))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
