import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
df = pd.read_csv('../results/qlearning_train_5000.csv', names=['episode','total_reward','epsilon','success'], header=0)
# if your file has header, adjust
# compute moving average
window = 20
ma = df['total_reward'].rolling(window).mean()
plt.figure(figsize=(6,3.2), dpi=200)
plt.plot(df['episode'], df['total_reward'], alpha=0.25, label='reward')
plt.plot(df['episode'], ma, linewidth=2, label=f'{window}-ep MA')
plt.xlabel('Episode')
plt.ylabel('Total Episode Reward')
plt.title('Q-Learning Learning Curve (5000 episodes)')
plt.legend()
plt.tight_layout()
os.makedirs('../results/plots', exist_ok=True)
plt.savefig('../results/plots/learning_curve_qlearning_train_5000.png')
