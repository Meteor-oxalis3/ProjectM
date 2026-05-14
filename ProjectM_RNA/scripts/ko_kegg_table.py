#!/micromamba/envs/ProjectM/bin/python
"""Generate interactive HTML table linking differential KOs to KEGG pathway pages."""
import argparse
import os

parser = argparse.ArgumentParser(description="DESeq2 KO results → KEGG HTML table")
parser.add_argument('-i', '--input', required=True, help='DESeq2 KO results TSV')
parser.add_argument('-o', '--outdir', required=True, help='Output directory')
parser.add_argument('--pval', type=float, default=0.05)
parser.add_argument('--log2fc', type=float, default=1.0)
args = parser.parse_args()

os.makedirs(args.outdir, exist_ok=True)

rows = []
with open(args.input) as f:
    header = f.readline().strip().split('\t')
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) < 7:
            continue
        baseMean, log2FC, lfcSE, pvalue, padj, ko_id, sig = parts[0:7]
        bm = float(baseMean)
        fc = float(log2FC)
        se = float(lfcSE)
        pv = float(pvalue)
        pa = float(padj) if padj not in ('NA', '') else None

        ko_num = ko_id.replace('ko:', '')
        if sig == 'Up':
            sig_html = f'<span class="up">↑ Up</span>'
        elif sig == 'Down':
            sig_html = f'<span class="down">↓ Down</span>'
        else:
            sig_html = '<span class="ns">NS</span>'

        rows.append({
            'ko': ko_id, 'ko_num': ko_num, 'baseMean': bm, 'log2FC': fc,
            'lfcSE': se, 'pvalue': pv, 'padj': pa, 'sig': sig, 'sig_html': sig_html,
            'kegg_entry': f"https://www.kegg.jp/entry/{ko_id}",
            'kegg_pathway': f"https://www.kegg.jp/kegg-bin/show_pathway?{ko_num}",
        })

rows.sort(key=lambda r: r['pvalue'])
sig_rows = [r for r in rows if r['sig'] != 'NS']
total_all = len(rows)
total_sig = len(sig_rows)
n_up = sum(1 for r in rows if r['sig'] == 'Up')
n_down = sum(1 for r in rows if r['sig'] == 'Down')

html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>KO 差异分析 — KEGG 查询表</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; background: #f5f5f5; }}
  h2 {{ color: #333; }}
  .info {{ color: #888; font-size: 14px; margin-bottom: 10px; }}
  table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  th {{ background: #1565C0; color: white; padding: 12px 16px; text-align: left; font-weight: 600; }}
  td {{ padding: 8px 14px; border-bottom: 1px solid #e0e0e0; font-size: 13px; }}
  tr:hover {{ background: #e3f2fd; }}
  a {{ color: #1565C0; text-decoration: none; font-weight: 500; }}
  a:hover {{ text-decoration: underline; }}
  .num {{ text-align: right; font-family: monospace; }}
  .up {{ color: #E07A5F; font-weight: bold; }}
  .down {{ color: #3D6B8F; font-weight: bold; }}
  .ns {{ color: #999; }}
  .pval {{ font-family: monospace; }}
  .filter-bar {{ margin-bottom: 12px; }}
  .filter-bar input {{ padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px; width: 300px; font-size: 14px; }}
  .filter-bar label {{ margin-right: 15px; font-size: 14px; cursor: pointer; }}
</style>
<script>
function filterTable() {{
  const q = document.getElementById('search').value.toLowerCase();
  document.querySelectorAll('tbody tr').forEach(tr => {{
    tr.style.display = (!q || tr.textContent.toLowerCase().includes(q)) ? '' : 'none';
  }});
}}
</script>
</head>
<body>
<h2>DESeq2 差异 KO — KEGG 功能查询</h2>
<p class="info">
  筛选条件: p &lt; {args.pval}, |log₂FC| &gt; {args.log2fc}，共 {total_sig} 个显著差异 KO（{n_up} ↑ / {n_down} ↓）。点击 KEGG 链接跳转至对应功能页面。
</p>
<div class="filter-bar">
  <input id="search" type="text" placeholder="搜索 KO 编号..." oninput="filterTable()">
</div>
<table>
<thead><tr>
  <th>KO ID</th><th>baseMean</th><th>log₂FC</th><th>lfcSE</th>
  <th>P-value</th><th>P-adj</th><th>方向</th>
  <th>KEGG 链接</th>
</tr></thead>
<tbody>
'''

for r in rows:
    if r['sig'] == 'NS':
        continue  # 默认不输出非显著 KO
    pa_str = f'{r["padj"]:.2e}' if r['padj'] is not None else 'NA'
    html += f'''<tr>
  <td><b>{r['ko_num']}</b></td>
  <td class="num">{r['baseMean']:.1f}</td>
  <td class="num">{r['log2FC']:+.2f}</td>
  <td class="num">{r['lfcSE']:.3f}</td>
  <td class="pval">{r['pvalue']:.2e}</td>
  <td class="pval">{pa_str}</td>
  <td>{r['sig_html']}</td>
  <td><a href="{r['kegg_entry']}" target="_blank">🔗 KEGG</a></td>
</tr>'''

html += '</tbody></table></body></html>'

outpath = os.path.join(args.outdir, 'ko_kegg_table.html')
with open(outpath, 'w') as f:
    f.write(html)
print(f"Generated {outpath} ({total_sig} sig / {total_all} total KOs)")
