#!/micromamba/envs/ProjectM/bin/python
"""Beta diversity: Bray-Curtis PCoA scatter plot."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.spatial.distance import pdist, squareform
from scipy.linalg import eigh
import argparse
import os

parser = argparse.ArgumentParser(description="Beta diversity PCoA")
parser.add_argument('-i', '--input', required=True, help='Relative abundance matrix TSV')
parser.add_argument('-m', '--metadata', required=True, help='Sample metadata CSV')
parser.add_argument('-o', '--outdir', required=True, help='Output directory')
args = parser.parse_args()

os.makedirs(args.outdir, exist_ok=True)

df = pd.read_csv(args.input, sep='\t', index_col=0)
meta = pd.read_csv(args.metadata)
group_dict = dict(zip(meta['ID'], meta['group']))
groups = sorted(meta['group'].unique())

# Species-level rows only
species_df = df[df.index.str.contains(r'\|s__[^|]+$') | df.index.str.match(r'^s__[^|]+$')]

# Samples as rows (samples × species matrix)
X = species_df.T

# ── Bray-Curtis distance matrix ───────────────────────────────────────────────
dist_vec = pdist(X.values, metric='braycurtis')
dist_matrix = squareform(dist_vec)
dist_df = pd.DataFrame(dist_matrix, index=X.index, columns=X.index)
dist_df.to_csv(f"{args.outdir}/bray_curtis_distance.tsv", sep='\t')

# ── Classical PCoA ────────────────────────────────────────────────────────────
n = dist_matrix.shape[0]
D2 = dist_matrix ** 2
J = np.eye(n) - np.ones((n, n)) / n
B = -0.5 * J @ D2 @ J

vals, vecs = eigh(B)
idx = np.argsort(vals)[::-1]
vals, vecs = vals[idx], vecs[:, idx]

pos_mask = vals > 1e-10
explained = vals[pos_mask] / vals[pos_mask].sum() * 100
coords = vecs[:, pos_mask] * np.sqrt(np.maximum(vals[pos_mask], 0))

pc1 = coords[:, 0]
pc2 = coords[:, 1] if coords.shape[1] > 1 else np.zeros(n)

# ── Colors ────────────────────────────────────────────────────────────────────
GROUP_COLORS = ['#E07A5F', '#3D6B8F', '#81B29A', '#F2CC8F']
color_map = {g: GROUP_COLORS[i % len(GROUP_COLORS)] for i, g in enumerate(groups)}

fig, ax = plt.subplots(figsize=(7, 6))

for g in groups:
    mask = np.array([group_dict.get(s) == g for s in X.index])
    ax.scatter(pc1[mask], pc2[mask], c=color_map[g], s=130, label=g,
               edgecolors='black', linewidth=0.8, zorder=3, alpha=0.9)

# Sample labels
for i, sample in enumerate(X.index):
    ax.annotate(sample, (pc1[i], pc2[i]),
                textcoords='offset points', xytext=(6, 4),
                fontsize=7, color='#333333')

ax.axhline(0, color='#AAAAAA', lw=0.8, ls='--')
ax.axvline(0, color='#AAAAAA', lw=0.8, ls='--')
ax.set_xlabel(f'PC1 ({explained[0]:.1f}%)', fontsize=11)
ax.set_ylabel(f'PC2 ({explained[1]:.1f}%)', fontsize=11)
ax.set_title('Beta Diversity – Bray-Curtis PCoA', fontsize=13, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(title='Group', frameon=False, fontsize=10, title_fontsize=10)

plt.tight_layout()
plt.savefig(f"{args.outdir}/beta_diversity_pcoa.pdf", dpi=300, bbox_inches='tight')
plt.savefig(f"{args.outdir}/beta_diversity_pcoa.png", dpi=150, bbox_inches='tight')
print(f"Beta diversity PCoA saved → {args.outdir}/beta_diversity_pcoa.pdf")
