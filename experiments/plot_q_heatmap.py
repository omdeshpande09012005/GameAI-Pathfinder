import numpy as np, matplotlib.pyplot as plt, os, csv
# path to policy file produced by QLearningAgent::savePolicy
policy = '../results/qpolicy_last.txt'  # save it from C++ by calling savePolicy
# parse keys: key = (y<<32)|(x<<16)|a as int64
def unpack_key(k):
    a = k & 0xFF
    x = (k>>16) & 0xFFFF
    y = (k>>32) & 0xFFFF
    return x,y,a

# load file
q = {}
with open(policy,'r') as f:
    for line in f:
        k,v = line.strip().split()
        k = int(k); v = float(v)
        x,y,a = unpack_key(k)
        q[(x,y,a)] = v

# build per-state best action value
xs = [p[0] for p in q.keys()]
ys = [p[1] for p in q.keys()]
W = max(xs)+1; H = max(ys)+1
best = np.full((H,W), np.nan)
for y in range(H):
    for x in range(W):
        vals = [ q.get((x,y,a), np.nan) for a in range(4) ]
        best[y,x] = np.nanmax(vals)
plt.figure(figsize=(4,4), dpi=200)
plt.imshow(best, origin='upper', cmap='viridis')
plt.colorbar(label='Best Q-value')
plt.title('Q-value Heatmap (best action per state)')
plt.tight_layout()
os.makedirs('../results/plots', exist_ok=True)
plt.savefig('../results/plots/q_value_heatmap.png')
