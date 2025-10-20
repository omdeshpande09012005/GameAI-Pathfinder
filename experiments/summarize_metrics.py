import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV = os.path.join(ROOT, "results", "metrics_all.csv")
OUT = os.path.join(ROOT, "results", "table_summary.csv")

df = pd.read_csv(CSV)
# ensure numeric
df['steps'] = pd.to_numeric(df['steps'], errors='coerce').fillna(0).astype(int)
df['time_ms'] = pd.to_numeric(df['time_ms'], errors='coerce').fillna(0.0)
df['success'] = pd.to_numeric(df['success'], errors='coerce').fillna(0).astype(int)

# group and aggregate
agg = df.groupby(['train_episodes','algo']).agg(
    runs=('success','count'),
    success_rate=('success','mean'),
    avg_steps=('steps','mean'),
    std_steps=('steps','std'),
    avg_time_ms=('time_ms','mean')
).reset_index()

# convert success_rate to percent
agg['success_rate'] = (agg['success_rate']*100).round(2)
agg['avg_steps'] = agg['avg_steps'].round(2)
agg['std_steps'] = agg['std_steps'].fillna(0).round(2)
agg.to_csv(OUT, index=False)
print("Wrote summary to", OUT)
print(agg)
