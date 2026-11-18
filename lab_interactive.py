"""The same interactive experiments in Colab, Jupyter, marimo and exported HTML.

Python supplies actual dataset rows and the fitted models. Controls and plots
run in the browser, so a saved HTML report keeps its controls without a kernel.
"""
from pathlib import Path
import json
import html
import uuid
import numpy as np
import pandas as pd
from IPython.display import HTML, display

ROOT = Path(__file__).resolve().parent
ENGINE = (ROOT / 'interactive_engine.js').read_text(encoding='utf-8')
CSS = '''
body{font:14px Arial,sans-serif;color:#203343;margin:0;background:white}
.lab-panel{padding:18px;border:1px solid #dce4e8;border-top:4px solid #ca839b;border-radius:12px;background:#fff}
.lab-controls{display:flex;flex-wrap:wrap;gap:16px;margin-bottom:15px;background:#f4f7f9;padding:16px;border-radius:8px}
.lab-controls label{display:flex;flex-direction:column;gap:7px;min-width:160px;font-size:12px;font-weight:600}
.lab-controls input,.lab-controls select{accent-color:#a13a54;max-width:230px;font:14px Arial;border-radius:5px}
.lab-controls select,.lab-controls input[type=number]{padding:7px;border:1px solid #b9cbd4;background:white;color:#203343}
.lab-controls output{font-variant-numeric:tabular-nums;color:#9b3854;min-height:15px}
.lab-note{line-height:1.6;background:#fff7ed;border-radius:6px;padding:8px 12px;margin:8px 0}
.lab-note:empty{display:none}.lab-metrics{overflow-x:auto;max-height:260px}.lab-metrics table{border-collapse:collapse;width:100%;font-size:12px;font-variant-numeric:tabular-nums}
.lab-metrics th{background:#203343;color:white;position:sticky;top:0}.lab-metrics th,.lab-metrics td{padding:8px 10px;text-align:left;border-bottom:1px solid #e3e9ed;white-space:nowrap}
.lab-metrics tr:nth-child(even){background:#f3f6f8}.lab-foot{font-size:12px;color:#566d7d;line-height:1.6;margin-top:10px}.lab-plot{min-height:450px}
'''

def _records(frame, keys=False):
    cols = [c for c in ['pH', 'residual sugar', 'alcohol', 'wine_type', 'carat', 'price', 'cut'] if c in frame]
    out = frame[cols].copy()
    if keys:
        out['_rowkey'] = pd.util.hash_pandas_object(frame, index=False).astype(str)
    return json.loads(out.to_json(orient='records', double_precision=12))

def payload(kind, namespace, **settings):
    diamond = kind in {'diamonds', 'diamond_pair', 'mass'}
    spec = {'kind': kind, **settings}
    need_data = kind in {'audit', 'split', 'eda', 'normality', 'pairs', 'welch', 'sample', 'consistency', 'diamonds', 'diamond_pair', 'mass'}
    spec['data'] = _records(namespace['diamonds' if diamond else 'df'], keys=kind in {'audit', 'split', 'welch'}) if need_data else []
    if kind in {'models', 'scale', 'generator', 'diagnostics', 'holdout', 'speed', 'gallery'}:
        spec['train'] = _records(namespace['train'])
    if kind in {'models', 'holdout'}:
        spec['holdout'] = _records(namespace['holdout'])
    if kind == 'models':
        spec['models'] = []
        for (group, col, name), model in namespace['fits'].items():
            row = namespace['fit_table'].query('тип == @group and величина == @col and модель == @name').iloc[0]
            spec['models'].append({'group':group, 'col':col, 'name':name,
                                  'pars':[float(x) for x in model.args],
                                  'bic':float(row.BIC_train), 'nll':float(row.NLL_holdout), 'ks':float(row.KS_D_holdout)})
    return spec

def panel_html(spec, full=False, offline=False):
    """Return an independent panel; offline=True bundles Plotly's JS locally."""
    if offline:
        from plotly.offline import get_plotlyjs
        library = '<script>' + get_plotlyjs() + '</script>'
    else:
        library = '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'
    ident = 'lab_' + uuid.uuid4().hex
    compact = dict(spec)
    for key in ['data', 'train', 'holdout']:
        records = spec.get(key)
        if records:
            columns = list(records[0])
            compact[key+'_columns'] = columns
            compact[key] = [[row[c] for c in columns] for row in records]
    data = json.dumps(compact, ensure_ascii=False, allow_nan=False, separators=(',', ':')).replace('</', '<\\/')
    body = f'<style>{CSS}</style>{library}<div class="lab-panel" id="{ident}"></div><script>{ENGINE}\nmountLab(document.getElementById("{ident}"),{data});</script>'
    return '<!doctype html><html lang="ru"><meta charset="utf-8">'+body+'</html>' if full else body

def show_interactive(kind, namespace, **settings):
    spec = payload(kind, namespace, **settings)
    fragment = panel_html(spec)
    display(HTML(fragment))
    return None

def iframe_html(spec):
    return '<iframe title="Интерактивное исследование" style="width:100%;height:880px;border:0" srcdoc="'+html.escape(panel_html(spec, full=True), quote=True)+'"></iframe>'
