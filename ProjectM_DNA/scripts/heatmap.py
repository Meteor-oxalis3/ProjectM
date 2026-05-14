#!/micromamba/envs/ProjectM/bin/python
"""Species heatmap with hierarchical clustering (top N by mean abundance)."""
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

parser = argparse.ArgumentParser(description="Species abundance heatmap")
parser.add_argument('-i', '--input',    required=True, help='Relative abundance matrix TSV')
parser.add_argument('-m', '--metadata', required=True, help='Sample metadata CSV')
parser.add_argument('-o', '--outdir',   required=True, help='Output directory')
parser.add_argument('-n', '--top_n',    type=int, default=30, help='Top N species [default: 30]')
args = parser.parse_args()

os.makedirs(args.outdir, exist_ok=True)

df = pd.read_csv(args.input, sep='\t', index_col=0)
meta = pd.read_csv(args.metadata)
group_dict = dict(zip(meta['ID'], meta['group']))
groups = sorted(meta['group'].unique())

# Species-level rows
species_df = df[df.index.str.contains(r'\|s__[^|]+$') | df.index.str.match(r'^s__[^|]+$')].copy()
species_df.index = species_df.index.str.replace(r'.*\|s__', 's__', regex=True)

# Top N by mean abundance across all samples
top_idx = species_df.mean(axis=1).nlargest(args.top_n).index
data = species_df.loc[top_idx].copy()

# Log10-transform for display (add small pseudocount)
data_log = np.log10(data + 1e-6)

# ── Hierarchical clustering on rows ──────────────────────────────────────────
row_dist = pdist(data_log.values, metric='euclidean')
row_link = linkage(row_dist, method='ward')
row_order = leaves_list(row_link)

# ── Sort columns by group ─────────────────────────────────────────────────────
cols_sorted = sorted(data.columns, key=lambda s: (group_dict.get(s, ''), s))
data_plot = data_log.iloc[row_order][cols_sorted]

# ── Colors ────────────────────────────────────────────────────────────────────
GROUP_COLORS = ['#E07A5F', '#3D6B8F', '#81B29A', '#F2CC8F']
color_map = {g: GROUP_COLORS[i % len(GROUP_COLORS)] for i, g in enumerate(groups)}

# ── Figure layout ─────────────────────────────────────────────────────────────
n_rows = len(data_plot)
n_cols = len(cols_sorted)
fig_w = max(7, n_cols * 0.7 + 2)
fig_h = max(6, n_rows * 0.32 + 1.5)

fig = plt.figure(figsize=(fig_w, fig_h))

# axes: [left, bottom, width, height] in figure fraction
left_margin  = 0.38
right_margin = 0.10
top_band     = 0.04   # group color bar height fraction
cb_width     = 0.025

heat_left   = left_margin
heat_bottom = 0.08
heat_width  = 1 - left_margin - right_margin - cb_width - 0.04
heat_height = 0.82

ax_heat  = fig.add_axes([heat_left, heat_bottom, heat_width, heat_height])
ax_group = fig.add_axes([heat_left, heat_bottom + heat_height + 0.005,
                          heat_width, top_band])
ax_cb    = fig.add_axes([heat_left + heat_width + 0.02,
                          heat_bottom, cb_width, heat_height])

# ── Draw heatmap ──────────────────────────────────────────────────────────────
vmin = data_plot.values.min()
vmax = data_plot.values.max()
im = ax_heat.imshow(data_plot.values, aspect='auto',
                    cmap='RdYlBu_r', vmin=vmin, vmax=vmax,
                    interpolation='nearest')

ax_heat.set_xticks(range(n_cols))
ax_heat.set_xticklabels(cols_sorted, rotation=45, ha='right', fontsize=10)
ax_heat.set_yticks(range(n_rows))
yticklabels = (data_plot.index
               .str.replace('s__', '', regex=False)
               .str.replace('_', ' ', regex=False))
ax_heat.set_yticklabels(yticklabels, fontsize=9, style='italic')
ax_heat.tick_params(axis='x', which='both', length=0)
ax_heat.tick_params(axis='y', which='both', length=0)

# ── Group color bar ───────────────────────────────────────────────────────────
for i, sample in enumerate(cols_sorted):
    g = group_dict.get(sample, groups[0])
    ax_group.add_patch(plt.Rectangle((i, 0), 1, 1, color=color_map[g], lw=0))
ax_group.set_xlim(0, n_cols)
ax_group.set_ylim(0, 1)
ax_group.axis('off')

# ── Colorbar ──────────────────────────────────────────────────────────────────
cbar = plt.colorbar(im, cax=ax_cb)
cbar.set_label('log₁₀(relative abundance)', fontsize=10)
cbar.ax.tick_params(labelsize=9)

# ── Legend ────────────────────────────────────────────────────────────────────
patches = [mpatches.Patch(color=color_map[g], label=g) for g in groups]
ax_heat.legend(handles=patches, title='Group', frameon=False,
               fontsize=10, title_fontsize=11,
               loc='upper left', bbox_to_anchor=(0, -0.18))

ax_group.set_title(f'Top {args.top_n} Species Heatmap',
                   fontsize=14, fontweight='bold', pad=6)

plt.savefig(f"{args.outdir}/heatmap.pdf", dpi=300, bbox_inches='tight')
plt.savefig(f"{args.outdir}/heatmap.png", dpi=150, bbox_inches='tight')
print(f"Heatmap saved → {args.outdir}/heatmap.pdf")
