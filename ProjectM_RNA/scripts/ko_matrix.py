#!/micromamba/envs/ProjectM/bin/python
"""Build KO abundance matrix from eggNOG-mapper annotations (KEGG_ko column)."""
import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser(description="Build KO count matrix from eggNOG-mapper annotations")
parser.add_argument('-a', '--annotations', nargs='+', required=True,
                    help='List of eggNOG .emapper.annotations files')
parser.add_argument('-o', '--output', required=True, help='Output KO count matrix TSV')
parser.add_argument('-r', '--relative', required=True, help='Output KO relative abundance matrix TSV')
parser.add_argument('-g', '--group_added', required=True, help='Output group-added matrix TSV')
parser.add_argument('-m', '--metadata', required=True, help='Sample metadata CSV')
args = parser.parse_args()

ko_counts = {}
for fpath in args.annotations:
    sample = os.path.basename(fpath).replace('.emapper.annotations', '')
    ko_counts[sample] = {}
    if not os.path.exists(fpath):
        print(f"Warning: {fpath} not found for sample {sample}")
        continue
    with open(fpath) as fh:
        lines = [l for l in fh if not l.startswith('##')]
    from io import StringIO
    raw = pd.read_csv(StringIO(''.join(lines)), sep='\t', header=None)
    raw = raw[~raw.iloc[:, 0].str.startswith('##')]
    raw.columns = raw.iloc[0].str.lstrip('#')
    df = raw.iloc[1:].reset_index(drop=True)
    if 'KEGG_ko' in df.columns:
        for kos in df['KEGG_ko'].dropna():
            for ko in str(kos).split(','):
                ko = ko.strip()
                if ko and ko != '-':
                    ko_counts[sample][ko] = ko_counts[sample].get(ko, 0) + 1

all_kos = sorted(set(ko for sc in ko_counts.values() for ko in sc))
# KOs as rows, samples as columns (consistent with species matrix convention)
ko_df = pd.DataFrame({s: {ko: ko_counts[s].get(ko, 0) for ko in all_kos} for s in ko_counts})
ko_df.index.name = 'KO'
ko_df.to_csv(args.output, sep='\t')

# Relative abundance: normalize by column (sample) total
ko_rel = ko_df.div(ko_df.sum(axis=0), axis=1).round(6)
ko_rel.to_csv(args.relative, sep='\t')

meta = pd.read_csv(args.metadata)
sample_to_group = dict(zip(meta['ID'], meta['group']))
group_row = [sample_to_group.get(s, "No_Group") for s in ko_rel.columns]
with open(args.group_added, 'w') as f:
    f.write("group\t" + "\t".join(group_row) + "\n")
    ko_rel.to_csv(f, sep='\t', index=True)

print(f"KO matrix built: {len(all_kos)} KOs × {len(ko_counts)} samples")
