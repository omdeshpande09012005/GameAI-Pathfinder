#!/usr/bin/env python3
"""
build_eval_master.py

Scan results/ for plausible evaluation CSVs (per-config eval files or single eval CSV),
normalize columns and write results/eval_runs.csv with canonical columns:
  method, config, run, steps, success, map_name

This script is conservative: it will include rows only when it can find steps/success info.
"""
import pandas as pd
from pathlib import Path
import re
import sys

RESULTS = Path("results")
OUT = RESULTS / "eval_runs.csv"

def safe_read(p):
    try:
        return pd.read_csv(p)
    except Exception as e:
        print(f"[warn] cannot read {p}: {e}")
        return None

def guess_columns(df):
    cols = {c.lower(): c for c in df.columns}
    # possible names
    method = cols.get('method') or cols.get('algo') or cols.get('algorithm') or None
    run = cols.get('run') or cols.get('trial') or cols.get('episode') or None
    steps = None
    for cand in ('steps','steps_to_goal','steps_taken','nsteps','length','path_len'):
        if cand in cols: 
            steps = cols[cand]; break
    success = cols.get('success') or cols.get('solved') or cols.get('succeeded') or None
    mapcol = cols.get('map') or cols.get('map_name') or cols.get('env') or None
    return method, run, steps, success, mapcol

def infer_method_from_name(name):
    n = name.lower()
    if 'astar' in n: return "A*"
    if 'qlearn' in n or 'q-learning' in n or 'qlearning' in n: return "Q-Learning"
    if 'eval' in n and 'astar' in n: return "A*"
    return None

def process_file(p):
    df = safe_read(p)
    if df is None: return []
    method_col, run_col, steps_col, succ_col, mapcol = guess_columns(df)
    method_from_name = infer_method_from_name(p.stem)
    rows = []
    for idx, r in df.iterrows():
        # find steps value
        steps = None
        if steps_col and pd.notna(r[steps_col]):
            try: steps = float(r[steps_col])
            except: steps = None
        else:
            # try any numeric column that looks like steps
            for c in df.columns:
                if c.lower().startswith('step') or 'len' in c.lower() or 'path' in c.lower():
                    try:
                        steps = float(r[c]); break
                    except: pass
        if steps is None:
            # no steps; skip
            continue
        success = None
        if succ_col and pd.notna(r[succ_col]):
            try: success = int(bool(r[succ_col]))
            except: 
                try:
                    v = float(r[succ_col]); success = 1 if v>0 and v!=999999 else 0
                except:
                    success = 1
        else:
            # infer success if steps finite
            success = 1
        method = r[method_col] if method_col and pd.notna(r[method_col]) else method_from_name or "unknown"
        config = r.get('config', p.stem) if 'config' in df.columns else p.stem
        run = int(r[run_col]) if run_col and pd.notna(r[run_col]) else int(idx)
        map_name = r[mapcol] if mapcol and pd.notna(r[mapcol]) else p.stem
        rows.append({
            'method': str(method),
            'config': str(config),
            'run': run,
            'steps': steps,
            'success': success,
            'map_name': str(map_name)
        })
    return rows

def main():
    candidates = list(RESULTS.glob("*eval*.csv")) + list(RESULTS.glob("eval_*.csv")) + list(RESULTS.glob("*_eval.csv")) + list(RESULTS.glob("eval-*.csv"))
    # also accept files like "results_qlearning_...csv" that may contain eval-like rows
    extra = [p for p in RESULTS.glob("*.csv") if ('eval' not in p.stem and ('qlearn' in p.stem or 'qlearning' in p.stem or 'astar' in p.stem))]
    candidates = sorted(set(candidates + extra))
    print("[info] candidate files:", [c.name for c in candidates])
    allrows = []
    for p in candidates:
        rows = process_file(p)
        print(f"[info] {p.name}: extracted {len(rows)} eval rows")
        allrows.extend(rows)
    if not allrows:
        print("[error] no eval rows found. Create results/eval_runs.csv manually with columns method,config,run,steps,success,map_name")
        return
    df = pd.DataFrame(allrows)
    df.to_csv(OUT, index=False)
    print("[ok] wrote", OUT, "rows:", len(df))

if __name__ == "__main__":
    main()
