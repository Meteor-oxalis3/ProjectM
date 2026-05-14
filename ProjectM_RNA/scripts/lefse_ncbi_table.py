#!/micromamba/envs/ProjectM/bin/python
"""Generate interactive HTML table linking LEfSe differential species to NCBI taxonomy pages."""
import argparse
import os
import urllib.parse

parser = argparse.ArgumentParser(description="LEfSe species → NCBI HTML table")
parser.add_argument('-i', '--input', required=True, help='LEfSe species LDA result file (.res)')
parser.add_argument('-o', '--outdir', required=True, help='Output directory')
parser.add_argument('-l', '--lda_threshold', type=float, default=2.0,
                    help='Minimum LDA score to include [default: 2.0]')
args = parser.parse_args()

os.makedirs(args.outdir, exist_ok=True)

rows = []
with open(args.input) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 5:
            continue
        taxonomy, lda_power, group, lda_score, pvalue = parts[0], parts[1], parts[2], parts[3], parts[4]

        # Skip entries without valid LDA
        try:
            lda_val = float(lda_score)
        except ValueError:
            continue
        if lda_val < args.lda_threshold or pvalue == '-':
            continue

        # Extract species name from taxonomy path (last s__ suffix)
        species = taxonomy.split('s__')[-1] if 's__' in taxonomy else taxonomy
        # Clean for NCBI search
        species_clean = species.replace('_', ' ').strip()

        # NCBI taxonomy URL
        ncbi_url = f"https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?name={urllib.parse.quote(species_clean)}"

        # Short display taxonomy (last 2-3 levels)
        levels = taxonomy.replace('d__', '|').replace('k__', '|').replace('p__', '|')
        levels = levels.replace('c__', '|').replace('o__', '|').replace('f__', '|')
        levels = levels.replace('g__', '|').replace('s__', '|')
        short_tax = ' | '.join([x for x in levels.split('|') if x.strip()][-3:]).strip()

        rows.append({
            'species': species_clean,
            'taxonomy': short_tax,
            'lda': lda_val,
            'pvalue': pvalue,
            'group': group,
            'ncbi_url': ncbi_url,
        })

# Sort by LDA descending
rows.sort(key=lambda r: r['lda'], reverse=True)

# HTML
html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>差异物种 NCBI 查询表</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; background: #f5f5f5; }}
  h2 {{ color: #333; }}
  table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  th {{ background: #1565C0; color: white; padding: 12px 16px; text-align: left; font-weight: 600; }}
  td {{ padding: 10px 16px; border-bottom: 1px solid #e0e0e0; }}
  tr:hover {{ background: #e3f2fd; }}
  a {{ color: #1565C0; text-decoration: none; font-weight: 500; }}
  a:hover {{ text-decoration: underline; }}
  .lda {{ font-weight: bold; }}
  .pval {{ font-family: monospace; color: #666; }}
  .group-UC {{ color: #E07A5F; font-weight: bold; }}
  .group-nonIBD {{ color: #3D6B8F; font-weight: bold; }}
  .info {{ color: #888; font-size: 14px; margin-bottom: 10px; }}
</style>
</head>
<body>
<h2>LEfSe 差异物种 — NCBI 分类学查询</h2>
<p class="info">LDA ≥ {args.lda_threshold}，共 {len(rows)} 个物种。点击 NCBI 链接跳转至对应分类学页面。</p>
<table>
<thead>
<tr>
  <th>物种 (Species)</th>
  <th>分类层级</th>
  <th>LDA Score</th>
  <th>P-value</th>
  <th>富集组</th>
  <th>NCBI 链接</th>
</tr>
</thead>
<tbody>
'''

for r in rows:
    group_class = 'group-UC' if r['group'] == 'UC' else 'group-nonIBD' if r['group'] == 'nonIBD' else ''
    html += f'''<tr>
  <td><i>{r['species']}</i></td>
  <td>{r['taxonomy']}</td>
  <td class="lda">{r['lda']:.2f}</td>
  <td class="pval">{r['pvalue']}</td>
  <td class="{group_class}">{r['group']}</td>
  <td><a href="{r['ncbi_url']}" target="_blank">🔗 NCBI</a></td>
</tr>
'''

html += '''</tbody></table></body></html>'''

outpath = os.path.join(args.outdir, 'lefse_ncbi_species.html')
with open(outpath, 'w') as f:
    f.write(html)
print(f"Generated {outpath} ({len(rows)} species)")
