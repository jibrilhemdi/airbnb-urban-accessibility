"""Compile current aggregate publication tables into LaTeX and an HTML report."""
import html
import pandas as pd
from src.ingestion.common import PROJECT_ROOT

def run():
    tables=PROJECT_ROOT/'outputs/tables/reporting';target=PROJECT_ROOT/'outputs/latex';target.mkdir(parents=True,exist_ok=True)
    sources=sorted(tables.glob('*.csv'))
    if not sources:raise RuntimeError('Current publication tables missing')
    latex=[];web=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Version 3 thesis results</title>',
        '<style>body{font:16px system-ui;max-width:1200px;margin:3rem auto}table{border-collapse:collapse;font-size:12px}td,th{padding:6px;border:1px solid #ddd}.scroll{overflow:auto}</style>',
        '<p><a href="reporting_figures_v3.html">Browse thesis figures · PNG</a></p><h1>Version 3 thesis results</h1><p>Core area context; eleven peer analysis areas; separate rail and bus accessibility. Conditional associations and held-out prediction.</p>']
    for path in sources:
        frame=pd.read_csv(path);name=path.stem
        (target/(name+'.tex')).write_text(frame.to_latex(index=False,escape=True,float_format=lambda x:f'{x:.4f}'))
        latex.append('\\input{'+name+'.tex}')
        web.extend(['<h2>'+html.escape(name.replace('_',' '))+'</h2><div class="scroll">',frame.to_html(index=False,escape=True),'</div>'])
    (target/'tables.tex').write_text('\n'.join(latex)+'\n')
    web.append('</html>');(PROJECT_ROOT/'reports/research_results_v3.html').write_text('\n'.join(web))
    return {'latex_tables':len(sources),'html_report':'reports/research_results_v3.html'}
