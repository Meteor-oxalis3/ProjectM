#!/micromamba/envs/ProjectM/bin/python
"""
Box plots for the top N LEfSe-significant species,
one subplot per species, colored by group.

LEfSe .res format (tab-separated, 5 columns):
  feature | log10_highest_avg | group | LDA_score | p_value
Feature names use '.' as separator; abundance matrix uses '|'.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import argparse
import os
import re

parser = argparse.ArgumentParser(description="Differential species box plots")
parser.add_argument('-i',  '--input',     required=True, help='Relative abundance matrix TSV')
parser.add_argument('-l',  '--lefse_res', required=True, help='LEfSe species LDA results file')
parser.add_argument('-m',  '--metadata',  required=True, help='Sample metadata CSV')
parser.add_argument('-o',  '--outdir',    required=True, help='Output directory')
parser.add_argument('-n',  '--top_n',     type=int, default=12,
                    help='Top N species by LDA score [default: 12]')
args = parser.parse_args()

os.makedirs(args.outdir, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
df   = pd.read_csv(args.input, sep='\t', index_col=0)
meta = pd.read_csv(args.metadata)
group_dict = dict(zip(meta['ID'], meta['group']))
groups = sorted(meta['group'].unique())

# ── Parse LEfSe results ───────────────────────────────────────────────────────
lefse = pd.read_csv(args.lefse_res, sep='\t', header=None,
                    names=['feature', 'log_avg', 'enriched_group', 'lda', 'pval'])
lefse = lefse.dropna(subset=['lda'])
lefse['lda'] = pd.to_numeric(lefse['lda'], errors='coerce')
lefse = lefse.dropna(subset=['lda']).sort_values('lda', ascending=False)
lefse_top = lefse.head(args.top_n)

# ── Match LEfSe feature names → abundance matrix index ───────────────────────
# LEfSe uses '.' as separator; matrix uses '|'
def dot_to_pipe(name):
    return name.replace('.', '|')

# Build lookup: pipe-separated name → original index row
pipe_index = {row: row for row in df.index}

matched_rows = []
for _, row in lefse_top.iterrows():
    pipe_name = dot_to_pipe(row['feature'])
    if pipe_name in pipe_index:
        matched_rows.append((row, pipe_name))
    else:
        # Fallback: match by species-level suffix
        suffix = re.search(r's__[^|.]+$', row['feature'])
        if suffix:
            candidates = [k for k in df.index if k.endswith(suffix.group())]
            if candidates:
                matched_rows.append((row, candidates[0]))

if not matched_rows:
    print("WARNING: No LEfSe features matched abundance matrix rows. Exiting.")
    exit(0)

# ── Colors ────────────────────────────────────────────────────────────────────
GROUP_COLORS = ['#E07A5F', '#3D6B8F', '#81B29A', '#F2CC8F']
color_map = {g: GROUP_COLORS[i % len(GROUP_COLORS)] for i, g in enumerate(groups)}

# ── Layout ────────────────────────────────────────────────────────────────────
n = len(matched_rows)
ncols = min(4, n)
nrows = (n + ncols - 1) // ncols
fig, axes = plt.subplots(nrows, ncols,
                         figsize=(ncols * 3.2, nrows * 3.5),
                         squeeze=False)
fig.suptitle('Top Differential Species (LEfSe)', fontsize=13,
             fontweight='bold', y=1.01)

np.random.seed(42)
for ax_idx, (lefse_row, matrix_key) in enumerate(matched_rows):
    r, c = divmod(ax_idx, ncols)
    ax = axes[r][c]

    abundances = df.loc[matrix_key]
    group_data = [abundances[[s for s in abundances.index
                              if group_dict.get(s) == g]].values
                  for g in groups]

    bp = ax.boxplot(
        group_data, patch_artist=True, widths=0.45,
        medianprops=dict(color='black', linewidth=2),
        whiskerprops=dict(linewidth=1.1),
        capprops=dict(linewidth=1.1),
        flierprops=dict(marker='o', markersize=3, markeredgecolor='gray'),
    )
    for patch, g in zip(bp['boxes'], groups):
        patch.set_facecolor(color_map[g])
        patch.set_alpha(0.75)

    for i, (g, data) in enumerate(zip(groups, group_data), 1):
        if len(data):
            jitter = np.random.uniform(-0.07, 0.07, size=len(data))
            ax.scatter(i + jitter, data, color=color_map[g],
                       s=45, zorder=4, edgecolors='black', linewidth=0.5)

    # Significance bracket
    if len(groups) == 2 and len(group_data[0]) > 0 and len(group_data[1]) > 0:
        _, pval = stats.mannwhitneyu(group_data[0], group_data[1], alternative='two-sided')
        pval_str = ('***' if pval < 0.001 else '**' if pval < 0.01
                    else '*' if pval < 0.05 else f'p={pval:.2f}')
        all_vals = np.concatenate([d for d in group_data if len(d)])
        y_top  = all_vals.max()
        y_span = all_vals.max() - all_vals.min()
        ax.plot([1, 1, 2, 2],
                [y_top + y_span*0.05, y_top + y_span*0.12,
                 y_top + y_span*0.12, y_top + y_span*0.05],
                color='black', lw=0.9)
        ax.text(1.5, y_top + y_span*0.13, pval_str,
                ha='center', va='bottom', fontsize=8)

    ax.set_xticks(range(1, len(groups) + 1))
    ax.set_xticklabels(groups, fontsize=8)
    ax.set_ylabel('Relative Abundance', fontsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Title: species name + enriched group + LDA score
    sp_name = re.search(r's__(.+)$', lefse_row['feature'])
    sp_name = sp_name.group(1).replace('_', ' ') if sp_name else lefse_row['feature']
    enrich  = lefse_row.get('enriched_group', '')
    lda_val = lefse_row.get('lda', '')
    ax.set_title(f"$\\it{{{sp_name}}}$\n[{enrich}, LDA={lda_val:.2f}]",
                 fontsize=7.5, pad=3)

# Hide unused subplots
for ax_idx in range(len(matched_rows), nrows * ncols):
    r, c = divmod(ax_idx, ncols)
    axes[r][c].set_visible(False)

patches = [mpatches.Patch(color=color_map[g], label=g, alpha=0.75) for g in groups]
fig.legend(handles=patches, loc='lower center', ncol=len(groups),
           bbox_to_anchor=(0.5, -0.03), frameon=False, fontsize=10)

plt.tight_layout()
plt.savefig(f"{args.outdir}/differential_boxplot.pdf", dpi=300, bbox_inches='tight')
plt.savefig(f"{args.outdir}/differential_boxplot.png", dpi=150, bbox_inches='tight')
print(f"Differential species box plots saved → {args.outdir}/differential_boxplot.pdf")
