#!/micromamba/envs/ProjectM/bin/python
"""KO abundance heatmap with hierarchical clustering (top N by mean abundance)."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import pdist
import argparse
import os

parser = argparse.ArgumentParser(description="KO abundance heatmap")
parser.add_argument('-i', '--input',    required=True, help='KO relative abundance matrix TSV (with group header row)')
parser.add_argument('-m', '--metadata', required=True, help='Sample metadata CSV')
parser.add_argument('-o', '--outdir',   required=True, help='Output directory')
parser.add_argument('-n', '--top_n',    type=int, default=30, help='Top N KOs [default: 30]')
args = parser.parse_args()

os.makedirs(args.outdir, exist_ok=True)

# Read matrix with group row
with open(args.input) as f:
    header = f.readline().strip().split('\t')
group_line = f.readline().strip().split('\t')

df = pd.read_csv(args.input, sep='\t', index_col=0, skiprows=1)
meta = pd.read_csv(args.metadata)
group_dict = dict(zip(meta['ID'], meta['group']))
groups = sorted(meta['group'].unique())

# Top N KOs by mean abundance
top_idx = df.mean(axis=1).nlargest(args.top_n).index
data = df.loc[top_idx].copy()

# Log10-transform
data_log = np.log10(data + 1e-6)

# Hierarchical clustering on rows
row_link = linkage(pdist(data_log.values, metric='euclidean'), method='ward')
row_order = leaves_list(row_link)

# Sort columns by group
cols_sorted = sorted(data.columns, key=lambda s: (group_dict.get(s, ''), s))
data_plot = data_log.iloc[row_order][cols_sorted]

# Colors
GROUP_COLORS = ['#E07A5F', '#3D6B8F', '#81B29A', '#F2CC8F']
color_map = {g: GROUP_COLORS[i % len(GROUP_COLORS)] for i, g in enumerate(groups)}

# Layout
n_rows, n_cols = len(data_plot), len(cols_sorted)
fig_w = max(9, n_cols * 1.1 + 3)
fig_h = max(8, n_rows * 0.38 + 2)

fig = plt.figure(figsize=(fig_w, fig_h))
left_margin, right_margin, top_band, cb_width = 0.32, 0.10, 0.04, 0.025
heat_l, heat_b, heat_w, heat_h = left_margin, 0.08, 1 - left_margin - right_margin - cb_width - 0.04, 0.82

ax_heat  = fig.add_axes([heat_l, heat_b, heat_w, heat_h])
ax_group = fig.add_axes([heat_l, heat_b + heat_h + 0.005, heat_w, top_band])
ax_cb    = fig.add_axes([heat_l + heat_w + 0.02, heat_b, cb_width, heat_h])

im = ax_heat.imshow(data_plot.values, aspect='auto', cmap='RdYlBu_r',
                    vmin=data_plot.values.min(), vmax=data_plot.values.max(), interpolation='nearest')
ax_heat.set_xticks(range(n_cols))
ax_heat.set_xticklabels(cols_sorted, rotation=45, ha='right', fontsize=8)
ax_heat.set_yticks(range(n_rows))
ax_heat.set_yticklabels(data_plot.index, fontsize=7.5)
ax_heat.tick_params(axis='both', which='both', length=0)

for i, sample in enumerate(cols_sorted):
    ax_group.add_patch(plt.Rectangle((i, 0), 1, 1, color=color_map[group_dict.get(sample, groups[0])], lw=0))
ax_group.set_xlim(0, n_cols)
ax_group.set_ylim(0, 1)
ax_group.axis('off')

cbar = plt.colorbar(im, cax=ax_cb)
cbar.set_label('log10(relative abundance)', fontsize=8)
cbar.ax.tick_params(labelsize=7)

patches = [mpatches.Patch(color=color_map[g], label=g) for g in groups]
ax_heat.legend(handles=patches, title='Group', frameon=False,
               fontsize=8, title_fontsize=9, loc='upper left', bbox_to_anchor=(0, -0.18))

ax_group.set_title(f'Top {args.top_n} KOs Heatmap', fontsize=12, fontweight='bold', pad=6)
plt.savefig(f"{args.outdir}/ko_heatmap.pdf", dpi=300, bbox_inches='tight')
plt.savefig(f"{args.outdir}/ko_heatmap.png", dpi=150, bbox_inches='tight')
print(f"KO heatmap saved -> {args.outdir}/ko_heatmap.pdf")
