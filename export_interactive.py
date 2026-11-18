"""Execute every cell, retain real results, export working offline controls."""
from pathlib import Path
import os, sys, json, re, base64, io, zipfile
import nbformat
from nbconvert import HTMLExporter
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.utils.capture import capture_output
from plotly.offline import get_plotlyjs

SUPPORT_FILES = [
    'lab_style.py', 'generators.py', 'app_marimo.py', 'test_lab.py',
    'test_interactive.py', 'requirements.txt', 'README.md', 'DEFENSE.md',
    'CHANGELOG.md', 'DATA_SOURCES.md', 'lab_interactive.py',
    'interactive_engine.js', 'interactive_context.py', 'export_interactive.py',
    'report_shell.py', 'report_ui.css', 'report_ui.js',
]

def refresh_support(notebook, root):
    """Keep Colab's embedded copy identical to this project's source files."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in SUPPORT_FILES:
            info = zipfile.ZipInfo(name, (2026, 11, 18, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (root / name).read_bytes())
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    setup = next(c for c in notebook.cells if c.metadata.get('id') == 'EXDs7hxgiL0M')
    setup.source, count = re.subn(r'_support = """.*?"""',
                                 '_support = """' + encoded + '"""',
                                 setup.source, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Не найдена встроенная копия модулей')

def validate_navigation(notebook):
    ids = {c.metadata['id'] for c in notebook.cells}
    numbers = []
    for cell in notebook.cells:
        if cell.cell_type != 'markdown':
            continue
        headings = re.findall(r'^#{1,6} (\d+(?:\.\d+)*) · ', cell.source, re.M)
        if len(headings) > 1:
            raise ValueError('Несколько нумерованных заголовков в одной ячейке')
        numbers.extend(headings)
        for target in re.findall(r'\]\(#scrollTo=([\w-]+)\)', cell.source):
            if target not in ids:
                raise ValueError('Не найден переход: ' + target)
        if '#contents)' in cell.source:
            raise ValueError('Осталась старая ссылка #contents')
    if len(numbers) != len(set(numbers)):
        raise ValueError('Повторяются номера разделов')

def main():
    import argparse
    parser=argparse.ArgumentParser(description="Экспорт интерактивного отчёта")
    parser.add_argument("--saved", action="store_true", help="Использовать сохранённые результаты без пересчёта")
    saved=parser.parse_args().saved
    root=Path(__file__).resolve().parent
    os.chdir(root)
    sys.path.insert(0,str(root))
    notebook=nbformat.read(root/'Lab01.ipynb',4)
    validate_navigation(notebook)
    refresh_support(notebook, root)
    shell=TerminalInteractiveShell.instance()
    shell.display_formatter.active_types=['text/plain','text/html','text/markdown','text/latex']
    count=sum(c.cell_type=='code' for c in notebook.cells) if saved else 0
    for i,cell in enumerate(notebook.cells):
        cell['id']=cell.metadata['id']
        if cell.cell_type!='code' or saved:continue
        count+=1
        with capture_output() as captured:
            result=shell.run_cell(cell.source,store_history=True)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError(f'Cell {i}: {result.error_before_exec or result.error_in_exec}\n{captured.stdout}\n{captured.stderr}')
        cell.outputs=[]
        if captured.stdout:cell.outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
        if captured.stderr:cell.outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
        for output in captured.outputs:
            cell.outputs.append(nbformat.v4.new_output('display_data',data=output.data,metadata=output.metadata))
        cell.outputs.insert(0,nbformat.v4.new_output('display_data',data={
            'text/html':'<a id="scrollTo='+cell.metadata['id']+'"></a>'},metadata={}))
        cell.execution_count=count
        print(f'Executed cell {i}',flush=True)
    nbformat.validate(notebook)
    nbformat.write(notebook,root/'Lab01.ipynb')
    # HTML uses exactly the executed outputs. Bundle Plotly once instead of CDN.
    export=nbformat.from_dict(json.loads(json.dumps(notebook)))
    for cell in export.cells:
        anchor='<a id="lab-cell-'+cell.metadata['id']+'"></a>'
        if cell.cell_type=='markdown':
            cell.source=anchor+'\n'+re.sub(r'#scrollTo=([\w-]+)',r'#lab-cell-\1',cell.source)
        else:
            cell.outputs.insert(0,nbformat.v4.new_output('display_data',data={'text/html':anchor},metadata={}))
            for output in cell.outputs:
                if 'data' in output and 'text/html' in output.data:
                    output.data['text/html']=output.data['text/html'].replace('<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>','')
    exporter=HTMLExporter()
    exporter.exclude_input=True
    exporter.exclude_input_prompt=True
    exporter.exclude_output_prompt=True
    html,_=exporter.from_notebook_node(export)
    html=html.replace('</head>','<script>'+get_plotlyjs()+'</script></head>',1)
    from report_shell import decorate_report
    html=decorate_report(html, notebook, root)
    # Navigation must survive future exports, including every return link.
    from html.parser import HTMLParser
    class Anchors(HTMLParser):
        def __init__(self):
            super().__init__(); self.ids=set(); self.targets=[]
        def handle_starttag(self, tag, attrs):
            attrs=dict(attrs)
            if 'id' in attrs:self.ids.add(attrs['id'])
            if tag=='a' and attrs.get('href','').startswith('#'):
                self.targets.append(attrs['href'][1:])
    links=Anchors(); links.feed(html)
    missing=set(links.targets)-links.ids
    if missing:raise ValueError('HTML: отсутствуют якоря '+repr(sorted(missing)))
    (root/'Lab01.html').write_text(html,encoding='utf-8')
    print('Completed:',count,'code cells; interactive panels:',html.count('mountLab(document.getElementById('))

if __name__=='__main__':main()
