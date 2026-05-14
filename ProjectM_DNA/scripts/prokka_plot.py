#!/micromamba/envs/ProjectM/bin/python
"""
Prokka annotation result visualization.

Reads Prokka .txt (feature counts) and .tsv (per-gene table) for one or more
groups and produces:
  1. Feature count comparison bar chart (CDS, tRNA, rRNA, etc.)
  2. Annotation rate donut charts (annotated vs hypothetical CDS)
  3. Top-20 functional products bar chart
  4. Shared / group-specific functions bubble chart (when ≥ 2 groups)
"""
import os, glob, re, argparse
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Wedge

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Prokka result visualizations")
parser.add_argument('-d', '--prokka_dir', required=True,
                    help='Parent directory containing one sub-dir per group '
                         '(e.g. output/XX/24_prokka/)')
parser.add_argument('-o', '--outdir',    required=True, help='Output directory')
parser.add_argument('-n', '--top_n',     type=int, default=20,
                    help='Top N gene products to show [default: 20]')
args = parser.parse_args()

os.makedirs(args.outdir, exist_ok=True)

# ── Color scheme ──────────────────────────────────────────────────────────────
GROUP_COLORS = ['#E07A5F', '#3D6B8F', '#81B29A', '#F2CC8F', '#9C89B8']

# ── 1. Parse .txt files → feature counts ─────────────────────────────────────
def parse_txt(txt_path):
    counts = {}
    with open(txt_path) as f:
        for line in f:
            line = line.strip()
            if ':' in line:
                k, v = line.split(':', 1)
                try:
                    counts[k.strip()] = int(v.strip())
                except ValueError:
                    counts[k.strip()] = v.strip()
    return counts

# ── 2. Parse .tsv files → per-gene table ─────────────────────────────────────
def parse_tsv(tsv_path):
    df = pd.read_csv(tsv_path, sep='\t')
    df.columns = df.columns.str.strip()
    return df

# ── Discover groups ───────────────────────────────────────────────────────────
txt_files = sorted(glob.glob(os.path.join(args.prokka_dir, '*', '*.txt')))
tsv_files = sorted(glob.glob(os.path.join(args.prokka_dir, '*', '*.tsv')))

if not txt_files:
    print(f"No .txt files found under {args.prokka_dir} — Prokka may not have finished yet.")
    exit(0)

groups      = [os.path.basename(os.path.dirname(f)) for f in txt_files]
color_map   = {g: GROUP_COLORS[i % len(GROUP_COLORS)] for i, g in enumerate(groups)}
feature_data = {g: parse_txt(f) for g, f in zip(groups, txt_files)}
tsv_data     = {}
for f in tsv_files:
    g = os.path.basename(os.path.dirname(f))
    tsv_data[g] = parse_tsv(f)

print(f"Groups found: {groups}")

# ═══════════════════════════════════════════════════════════════════════════════
# Plot 1 — Feature count grouped bar chart
# ═══════════════════════════════════════════════════════════════════════════════
feature_keys = ['CDS', 'tRNA', 'rRNA', 'tmRNA', 'repeat_region',
                'misc_RNA', 'sig_peptide']
feature_keys = [k for k in feature_keys
                if any(k in feature_data[g] for g in groups)]

fig, ax = plt.subplots(figsize=(max(6, len(feature_keys) * 1.2), 4))
x        = np.arange(len(feature_keys))
bar_w    = 0.8 / max(len(groups), 1)
offsets  = np.linspace(-(len(groups)-1)/2 * bar_w,
                        (len(groups)-1)/2 * bar_w, len(groups))

for g, offset in zip(groups, offsets):
    vals = [feature_data[g].get(k, 0) for k in feature_keys]
    bars = ax.bar(x + offset, vals, width=bar_w * 0.9,
                  label=g, color=color_map[g], alpha=0.85, edgecolor='white')
    for bar, v in zip(bars, vals):
        if v:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(vals)*0.01,
                    f'{v:,}', ha='center', va='bottom', fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels(feature_keys, fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('Prokka Annotation — Feature Counts by Group', fontsize=14, fontweight="bold")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(frameon=False, fontsize=12)
plt.tight_layout()
plt.savefig(f"{args.outdir}/prokka_feature_counts.pdf", dpi=300, bbox_inches='tight')
plt.savefig(f"{args.outdir}/prokka_feature_counts.png", dpi=150, bbox_inches='tight')
plt.close()
print("Plot 1 done: feature counts")

# ═══════════════════════════════════════════════════════════════════════════════
# Plot 2 — Annotation rate donut charts
# ═══════════════════════════════════════════════════════════════════════════════
if tsv_data:
    n_groups = len(groups)
    fig, axes = plt.subplots(1, n_groups, figsize=(4 * n_groups, 4))
    if n_groups == 1:
        axes = [axes]

    for ax, g in zip(axes, groups):
        if g not in tsv_data:
            ax.set_visible(False)
            continue
        df = tsv_data[g]
        cds = df[df['ftype'] == 'CDS'] if 'ftype' in df.columns else df
        total = len(cds)
        if total == 0:
            ax.set_visible(False)
            continue

        hypo  = cds['product'].str.lower().str.contains('hypothetical', na=False).sum() \
                if 'product' in cds.columns else 0
        annot = total - hypo

        sizes  = [annot, hypo]
        labels = [f'Annotated\n{annot:,} ({annot/total*100:.1f}%)',
                  f'Hypothetical\n{hypo:,} ({hypo/total*100:.1f}%)']
        colors = [color_map[g], '#CCCCCC']

        wedges, _ = ax.pie(
            sizes, labels=None, colors=colors,
            startangle=90, wedgeprops=dict(width=0.55, edgecolor='white', linewidth=2)
        )
        ax.set_title(g, fontsize=14, fontweight="bold", pad=10)
        ax.text(0, 0, f'{total:,}\nCDS', ha='center', va='center',
                fontsize=11, fontweight='bold')

        patches = [mpatches.Patch(color=c, label=l)
                   for c, l in zip(colors, labels)]
        ax.legend(handles=patches, loc='lower center',
                  bbox_to_anchor=(0.5, -0.18), frameon=False, fontsize=12)

    fig.suptitle('CDS Annotation Rate', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{args.outdir}/prokka_annotation_rate.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(f"{args.outdir}/prokka_annotation_rate.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("Plot 2 done: annotation rate donuts")

# ═══════════════════════════════════════════════════════════════════════════════
# Plot 3 — Top N functional products (per group, excluding hypothetical)
# ═══════════════════════════════════════════════════════════════════════════════
if tsv_data:
    n_groups = len(groups)
    fig, axes = plt.subplots(1, n_groups,
                              figsize=(7 * n_groups, max(6, args.top_n * 0.32)))
    if n_groups == 1:
        axes = [axes]

    for ax, g in zip(axes, groups):
        if g not in tsv_data:
            ax.set_visible(False)
            continue
        df  = tsv_data[g]
        cds = df[df['ftype'] == 'CDS'] if 'ftype' in df.columns else df
        if 'product' not in cds.columns:
            ax.set_visible(False)
            continue

        top = (cds[~cds['product'].str.lower().str.contains('hypothetical', na=False)]
               ['product'].value_counts().head(args.top_n))
        if top.empty:
            ax.set_visible(False)
            continue

        bars = ax.barh(range(len(top)), top.values, color=color_map[g], alpha=0.85,
                       edgecolor='white')
        ax.set_yticks(range(len(top)))
        ax.set_yticklabels(top.index, fontsize=12)
        ax.invert_yaxis()
        ax.set_xlabel('Gene count', fontsize=12)
        ax.set_title(f'Top {args.top_n} Functional Products\n({g})',
                     fontsize=13, fontweight="bold")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for bar, v in zip(bars, top.values):
            ax.text(v + top.values.max()*0.01, bar.get_y() + bar.get_height()/2,
                    str(v), va='center', fontsize=8)

    plt.tight_layout()
    plt.savefig(f"{args.outdir}/prokka_top_products.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(f"{args.outdir}/prokka_top_products.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("Plot 3 done: top products")

# ═══════════════════════════════════════════════════════════════════════════════
# Plot 4 — Shared / group-specific functions bubble chart (≥ 2 groups)
# ═══════════════════════════════════════════════════════════════════════════════
if len(tsv_data) >= 2 and all('product' in tsv_data[g].columns for g in tsv_data):
    # Build product count per group (non-hypothetical CDS only)
    product_counts = {}
    for g in groups:
        if g not in tsv_data:
            continue
        df  = tsv_data[g]
        cds = df[df['ftype'] == 'CDS'] if 'ftype' in df.columns else df
        cnts = (cds[~cds['product'].str.lower().str.contains('hypothetical', na=False)]
                ['product'].value_counts())
        product_counts[g] = cnts

    # Union of top products across all groups
    all_top = set()
    for g, cnts in product_counts.items():
        all_top.update(cnts.head(30).index.tolist())
    all_top = sorted(all_top)

    if all_top and len(groups) == 2:
        g0, g1 = groups[0], groups[1]
        c0 = product_counts.get(g0, pd.Series(dtype=float))
        c1 = product_counts.get(g1, pd.Series(dtype=float))

        x_vals = [c0.get(p, 0) for p in all_top]
        y_vals = [c1.get(p, 0) for p in all_top]
        total  = [x + y for x, y in zip(x_vals, y_vals)]
        sizes  = [max(20, t * 6) for t in total]

        fig, ax = plt.subplots(figsize=(6, 5.5))
        sc = ax.scatter(x_vals, y_vals, s=sizes, alpha=0.65,
                        c=total, cmap='YlOrRd', edgecolors='gray', linewidths=0.5)

        # Label top points
        paired = sorted(zip(total, all_top, x_vals, y_vals), reverse=True)
        for rank, (tot, prod, xv, yv) in enumerate(paired[:15]):
            short = prod[:35] + '…' if len(prod) > 35 else prod
            ax.annotate(short, (xv, yv), textcoords='offset points',
                        xytext=(5, 4), fontsize=8, color='#333333')

        diag = max(max(x_vals), max(y_vals)) * 1.05
        ax.plot([0, diag], [0, diag], 'k--', lw=0.8, alpha=0.4, label='equal')
        ax.set_xlabel(f'{g0} gene count', fontsize=12)
        ax.set_ylabel(f'{g1} gene count', fontsize=12)
        ax.set_title('Shared & Group-Enriched Functional Products',
                     fontsize=13, fontweight="bold")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.colorbar(sc, ax=ax, label='Total count', shrink=0.7)
        plt.tight_layout()
        plt.savefig(f"{args.outdir}/prokka_product_bubble.pdf", dpi=300, bbox_inches='tight')
        plt.savefig(f"{args.outdir}/prokka_product_bubble.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("Plot 4 done: product bubble chart")

print(f"\nAll Prokka plots saved to {args.outdir}/")
