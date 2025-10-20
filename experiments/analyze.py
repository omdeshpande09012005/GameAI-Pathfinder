# experiments/analyze.py
import os, glob
import pandas as pd
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV = os.path.join(ROOT, "results", "metrics_all.csv")
OUTDIR = os.path.join(ROOT, "results", "plots")
os.makedirs(OUTDIR, exist_ok=True)

# Read combined metrics if exists, otherwise fallback to metrics.csv
if os.path.exists(CSV):
    df = pd.read_csv(CSV)
else:
    CSV2 = os.path.join(ROOT, "results", "metrics.csv")
    if not os.path.exists(CSV2):
        print("No metrics CSV found.")
        raise SystemExit(1)
    df = pd.read_csv(CSV2)

# basic clean
df.columns = df.columns.str.strip()
df['steps'] = pd.to_numeric(df['steps'], errors='coerce').fillna(0).astype(int)
df['time_ms'] = pd.to_numeric(df['time_ms'], errors='coerce').fillna(0.0)
df['success'] = pd.to_numeric(df['success'], errors='coerce').fillna(0).astype(int)

# Path length comparison
plt.figure(figsize=(6,4))
groups = [df[df['algo']=='astar']['steps'], df[df['algo']=='qlearn']['steps']]
labels = ['A*','Q-Learn']
plt.boxplot(groups, labels=labels, showmeans=True)
plt.title('Path Length (steps) — A* vs Q-Learn')
plt.ylabel('Steps')
plt.grid(axis='y', alpha=0.4)
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "path_length_comparison.png"), dpi=200)
plt.close()

# Success rate vs training episodes (if available)
if 'train_episodes' in df.columns:
    pivot = df.groupby(['train_episodes','algo'])['success'].mean().unstack().fillna(0)*100
    pivot.plot(kind='bar', figsize=(8,4))
    plt.title('Success Rate (%) vs Training Episodes')
    plt.ylabel('Success rate (%)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "success_rate_vs_train.png"), dpi=200)
    plt.close()

# Steps per run scatter
plt.figure(figsize=(7,4))
for algo, g in df.groupby('algo'):
    plt.scatter(g['run'], g['steps'], label=algo, s=80, alpha=0.9)
plt.title('Steps per Run')
plt.xlabel('Run index')
plt.ylabel('Steps')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "steps_per_run.png"), dpi=200)
plt.close()

# Learning curve plots: find qlearning_train_*.csv
train_logs = sorted(glob.glob(os.path.join(ROOT,"results","qlearning_train_*.csv")))
for tl in train_logs:
    tdf = pd.read_csv(tl)
    # ensure numeric
    tdf['episode'] = pd.to_numeric(tdf['episode'], errors='coerce')
    tdf['total_reward'] = pd.to_numeric(tdf['total_reward'], errors='coerce')
    if tdf.empty:
        continue
    plt.figure(figsize=(8,4))
    plt.plot(tdf['episode'], tdf['total_reward'], alpha=0.6)
    # moving average for smoothness
    if len(tdf) >= 20:
        tdf['ma'] = tdf['total_reward'].rolling(window=20, min_periods=1).mean()
        plt.plot(tdf['episode'], tdf['ma'], linewidth=2, label='20-ep MA')
    plt.title(f'Learning Curve - {os.path.basename(tl)}')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    outfn = os.path.join(OUTDIR, f"learning_curve_{os.path.basename(tl).replace('.csv','.png')}")
    plt.savefig(outfn, dpi=200)
    plt.close()

print("Analysis complete. Plots in", OUTDIR)
