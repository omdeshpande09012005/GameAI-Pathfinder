import pandas as pd, matplotlib.pyplot as plt, os
df = pd.read_csv('../results/metrics_all.csv')
# group by train_episodes and algo
grp = df.groupby(['train_episodes','algo']).agg(success_rate=('success','mean')).reset_index()
pivot = grp.pivot(index='train_episodes', columns='algo', values='success_rate')
plt.figure(figsize=(6,3), dpi=200)
for col in pivot.columns:
    plt.plot(pivot.index, pivot[col]*100, marker='o', label=col)
plt.xlabel('Training Episodes')
plt.ylabel('Success Rate (%)')
plt.title('Success Rate vs Training Episodes')
plt.xticks(pivot.index)
plt.legend()
plt.tight_layout()
os.makedirs('../results/plots', exist_ok=True)
plt.savefig('../results/plots/success_rate_vs_train.png')
