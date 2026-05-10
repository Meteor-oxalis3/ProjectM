#!/micromamba/envs/ProjectM/bin/python
"""Alpha diversity analysis: Shannon, Simpson, Observed Species box plots."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import argparse
import os

parser = argparse.ArgumentParser(description="Alpha diversity analysis")
parser.add_argument('-i', '--input', required=True, help='Relative abundance matrix TSV (rows=taxa, cols=samples)')
parser.add_argument('-m', '--metadata', required=True, help='Sample metadata CSV with ID and group columns')
parser.add_argument('-o', '--outdir', required=True, help='Output directory')
args = parser.parse_args()

os.makedirs(args.outdir, exist_ok=True)

df = pd.read_csv(args.input, sep='\t', index_col=0)
meta = pd.read_csv(args.metadata)
group_dict = dict(zip(meta['ID'], meta['group']))
groups = sorted(meta['group'].unique())

# Species-level rows: must contain s__ as the deepest taxonomic level
species_df = df[df.index.str.contains(r'\|s__[^|]+$') | df.index.str.match(r'^s__[^|]+$')]

# Diversity metrics
def shannon(col):
    p = col[col > 0]
    return float(-np.sum(p * np.log(p))) if len(p) > 0 else 0.0

def simpson(col):
    p = col[col > 0]
    return float(1 - np.sum(p ** 2)) if len(p) > 0 else 0.0

def observed_species(col):
    return int((col > 0).sum())

records = []
for sample in species_df.columns:
    col = species_df[sample]
    records.append({
        'SampleID': sample,
        'group': group_dict.get(sample, 'Unknown'),
        'Shannon': shannon(col),
        'Simpson': simpson(col),
        'Observed_Species': observed_species(col),
    })

diversity_df = pd.DataFrame(records).set_index('SampleID')
diversity_df.to_csv(f"{args.outdir}/alpha_diversity.tsv", sep='\t')

# ── Colors ────────────────────────────────────────────────────────────────────
GROUP_COLORS = ['#E07A5F', '#3D6B8F', '#81B29A', '#F2CC8F']
color_map = {g: GROUP_COLORS[i % len(GROUP_COLORS)] for i, g in enumerate(groups)}

# ── Plot ──────────────────────────────────────────────────────────────────────
metrics = ['Shannon', 'Simpson', 'Observed_Species']
labels  = ['Shannon Diversity Index', "Simpson's Diversity Index", 'Observed Species']

fig, axes = plt.subplots(1, 3, figsize=(13, 5))
fig.suptitle('Alpha Diversity by Group', fontsize=14, fontweight='bold', y=1.02)

np.random.seed(42)
for ax, metric, label in zip(axes, metrics, labels):
    group_data = [diversity_df[diversity_df['group'] == g][metric].values for g in groups]

    bp = ax.boxplot(
        group_data, patch_artist=True, widths=0.45,
        medianprops=dict(color='black', linewidth=2),
        whiskerprops=dict(linewidth=1.2),
        capprops=dict(linewidth=1.2),
        flierprops=dict(marker='o', markersize=4, markeredgecolor='gray'),
    )
    for patch, g in zip(bp['boxes'], groups):
        patch.set_facecolor(color_map[g])
        patch.set_alpha(0.75)

    for i, (g, data) in enumerate(zip(groups, group_data), 1):
        jitter = np.random.uniform(-0.07, 0.07, size=len(data))
        ax.scatter(i + jitter, data, color=color_map[g],
                   s=55, zorder=4, edgecolors='black', linewidth=0.6)

    # Mann-Whitney U for 2 groups; Kruskal-Wallis otherwise
    if len(groups) == 2 and len(group_data[0]) > 0 and len(group_data[1]) > 0:
        _, pval = stats.mannwhitneyu(group_data[0], group_data[1], alternative='two-sided')
        pval_str = f'p = {pval:.3f}' if pval >= 0.001 else 'p < 0.001'
        y_top = max(max(d) for d in group_data if len(d))
        y_range = y_top - min(min(d) for d in group_data if len(d))
        ax.plot([1, 1, 2, 2],
                [y_top + y_range * 0.05, y_top + y_range * 0.12,
                 y_top + y_range * 0.12, y_top + y_range * 0.05],
                color='black', lw=1)
        ax.text(1.5, y_top + y_range * 0.14, pval_str,
                ha='center', va='bottom', fontsize=9, style='italic')

    ax.set_xticks(range(1, len(groups) + 1))
    ax.set_xticklabels(groups, fontsize=10)
    ax.set_ylabel(label, fontsize=10)
    ax.set_title(label, fontsize=11, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

patches = [mpatches.Patch(color=color_map[g], label=g, alpha=0.75) for g in groups]
fig.legend(handles=patches, loc='lower center', ncol=len(groups),
           bbox_to_anchor=(0.5, -0.06), frameon=False, fontsize=10)

plt.tight_layout()
plt.savefig(f"{args.outdir}/alpha_diversity.pdf", dpi=300, bbox_inches='tight')
plt.savefig(f"{args.outdir}/alpha_diversity.png", dpi=150, bbox_inches='tight')
print(f"Alpha diversity saved → {args.outdir}/alpha_diversity.pdf")
