#!/micromamba/envs/ProjectM/bin/python
"""KO volcano plot: log2 fold change vs -log10 p-value between two groups."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import argparse
import os

parser = argparse.ArgumentParser(description="KO differential volcano plot")
parser.add_argument('-i', '--input',    required=True, help='KO count matrix TSV (no group header)')
parser.add_argument('-m', '--metadata', required=True, help='Sample metadata CSV')
parser.add_argument('-o', '--outdir',   required=True, help='Output directory')
parser.add_argument('--pval',           type=float, default=0.05, help='P-value threshold [default: 0.05]')
parser.add_argument('--log2fc',         type=float, default=1.0, help='|log2FC| threshold [default: 1.0]')
args = parser.parse_args()

os.makedirs(args.outdir, exist_ok=True)

df = pd.read_csv(args.input, sep='\t', index_col=0)
meta = pd.read_csv(args.metadata)
group_dict = dict(zip(meta['ID'], meta['group']))
groups = sorted(meta['group'].unique())

if len(groups) != 2:
    print(f"ERROR: Volcano plot requires exactly 2 groups, found {len(groups)}: {groups}")
    exit(1)

g1, g2 = groups
samples_g1 = [s for s in df.columns if group_dict.get(s) == g1]
samples_g2 = [s for s in df.columns if group_dict.get(s) == g2]

print(f"Group {g1}: {len(samples_g1)} samples, Group {g2}: {len(samples_g2)} samples")

results = []
for ko in df.index:
    vals_g1 = df.loc[ko, samples_g1].values.astype(float)
    vals_g2 = df.loc[ko, samples_g2].values.astype(float)

    mean_g1 = vals_g1.mean()
    mean_g2 = vals_g2.mean()

    log2fc = np.log2(mean_g1 + 1e-6) - np.log2(mean_g2 + 1e-6)

    if len(vals_g1) > 1 and len(vals_g2) > 1:
        try:
            _, pval = stats.mannwhitneyu(vals_g1, vals_g2, alternative='two-sided')
        except ValueError:
            pval = 1.0
    else:
        pval = 1.0

    results.append({'KO': ko, 'log2FC': log2fc, 'pvalue': pval,
                    'mean_g1': mean_g1, 'mean_g2': mean_g2})

res_df = pd.DataFrame(results)
res_df['neg_log10_p'] = -np.log10(res_df['pvalue'].clip(lower=1e-300))

# Significance categories
res_df['sig'] = 'NS'
res_df.loc[(res_df['pvalue'] < args.pval) & (res_df['log2fc'] >= args.log2fc), 'sig'] = 'Up'
res_df.loc[(res_df['pvalue'] < args.pval) & (res_df['log2fc'] <= -args.log2fc), 'sig'] = 'Down'

# Save results table
res_df.to_csv(f"{args.outdir}/ko_diff_results.tsv", sep='\t', index=False)

# Plot
fig, ax = plt.subplots(figsize=(10, 8))

colors = {'NS': '#999999', 'Up': '#E07A5F', 'Down': '#3D6B8F'}
for cat, c in colors.items():
    subset = res_df[res_df['sig'] == cat]
    ax.scatter(subset['log2FC'], subset['neg_log10_p'], c=c, label=cat, s=15, alpha=0.7, edgecolors='none')

# Label top significant KOs
top_hits = res_df[res_df['sig'] != 'NS'].nlargest(15, 'neg_log10_p')
for _, row in top_hits.iterrows():
    ax.annotate(row['KO'].replace('ko:', ''), (row['log2FC'], row['neg_log10_p']),
                fontsize=6, alpha=0.9, ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.6, lw=0))

# Threshold lines
max_y = res_df['neg_log10_p'].max() * 1.1
ax.axhline(-np.log10(args.pval), color='grey', linestyle='--', linewidth=0.8, alpha=0.6)
ax.axvline(args.log2fc, color='grey', linestyle='--', linewidth=0.8, alpha=0.6)
ax.axvline(-args.log2fc, color='grey', linestyle='--', linewidth=0.8, alpha=0.6)

ax.set_xlabel(f'log$_2$(Fold Change) [{g1} / {g2}]', fontsize=12)
ax.set_ylabel('-log$_{10}$(p-value)', fontsize=12)
ax.set_title(f'KO Differential Abundance: {g1} vs {g2}', fontsize=13, fontweight='bold')

ax.legend(fontsize=9, frameon=False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(f"{args.outdir}/ko_volcano.pdf", dpi=300, bbox_inches='tight')
plt.savefig(f"{args.outdir}/ko_volcano.png", dpi=150, bbox_inches='tight')
print(f"KO volcano plot saved -> {args.outdir}/ko_volcano.pdf")
print(f"Differential KOs: Up={sum(res_df['sig']=='Up')}, Down={sum(res_df['sig']=='Down')}, NS={sum(res_df['sig']=='NS')}")
