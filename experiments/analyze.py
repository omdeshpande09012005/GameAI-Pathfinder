# experiments/analyze.py
# Usage: python experiments/analyze.py
# Produces PNG plots in results/plots/

import os
import pandas as pd
import matplotlib.pyplot as plt
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV = os.path.join(ROOT, "results", "metrics.csv")
OUTDIR = os.path.join(ROOT, "results", "plots")
os.makedirs(OUTDIR, exist_ok=True)

if not os.path.exists(CSV):
    print("CSV not found:", CSV)
    sys.exit(1)

# Read CSV defensively
df = pd.read_csv(CSV, dtype=str)         # read as strings first
# clean column names (strip BOM/whitespace)
df.columns = df.columns.str.strip().str.replace('\ufeff', '')

# Show head for debug
print("CSV Columns:", list(df.columns))
print("CSV Head:")
print(df.head())

# Try to coerce expected columns
for col in ['steps', 'time_ms', 'success', 'run']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        print(f"Warning: expected column '{col}' not found in CSV.")
        # create a default column to avoid crashes later
        if col == 'steps' or col == 'run':
            df[col] = 0
        else:
            df[col] = 0.0

# normalize algo column
if 'algo' in df.columns:
    df['algo'] = df['algo'].astype(str).str.strip().str.lower()
else:
    print("Error: 'algo' column missing. CSV must include 'algo' column.")
    sys.exit(1)

# 1) Path length comparison (boxplot)
plt.figure(figsize=(6,4))
group_df = df.groupby('algo')
astar_steps = group_df.get_group('astar')['steps'] if 'astar' in group_df.groups else pd.Series([], dtype=float)
qlearn_steps = group_df.get_group('qlearn')['steps'] if 'qlearn' in group_df.groups else pd.Series([], dtype=float)

plt.boxplot([astar_steps.dropna(), qlearn_steps.dropna()], labels=['A*','Q-Learn'], showmeans=True)
plt.title('Path Length (steps) — A* vs Q-Learn')
plt.ylabel('Steps')
plt.grid(axis='y', alpha=0.4)
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "path_length_comparison.png"), dpi=200)
plt.close()

# 2) Success rate (bar)
succ = df.groupby('algo')['success'].mean() * 100.0
plt.figure(figsize=(5,4))
succ.plot(kind='bar')
plt.title('Success Rate (%)')
plt.ylabel('Success rate (%)')
plt.ylim(0,100)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "success_rate.png"), dpi=200)
plt.close()

# 3) Steps per run (scatter)
plt.figure(figsize=(7,4))
for algo, g in df.groupby('algo'):
    plt.scatter(g['run'] + (0 if algo=='astar' else 0.1), g['steps'], label=algo, s=80, alpha=0.9)
plt.title('Steps per Run')
plt.xlabel('Run index')
plt.ylabel('Steps')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "steps_per_run.png"), dpi=200)
plt.close()

print("Plots saved to", OUTDIR)
