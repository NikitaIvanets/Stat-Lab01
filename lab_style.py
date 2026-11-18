"""Оформление отчёта: отдельно от статистических расчётов."""
from IPython.display import display, HTML
CSS = '''
<style>
:root {--ink:#203343;--muted:#647582;--wine:#9b3854;--paper:#faf9f6;}
.jp-RenderedHTMLCommon,.text_cell_render {line-height:1.7;color:var(--ink);}
.jp-RenderedHTMLCommon h1 {border-top:3px solid var(--wine);padding-top:26px;margin-top:64px;letter-spacing:-.025em;}
.jp-RenderedHTMLCommon h2 {margin-top:34px;letter-spacing:-.02em;}
.jp-RenderedHTMLCommon a {color:#345c80;}
.jp-RenderedHTMLCommon table {font-size:13px;border-collapse:collapse;}
.jp-RenderedHTMLCommon th {background:#edf1f3;padding:10px;text-align:left;}
.jp-RenderedHTMLCommon td {padding:8px;border-bottom:1px solid #dce2e5;}
.lab-cover {background:#203343;color:#fff;padding:48px;border-radius:14px;margin:20px 0 32px;}
.lab-cover .eyebrow {letter-spacing:.18em;font-size:12px;color:#e8bbc9;}
.lab-cover .title {font-size:clamp(32px,5vw,54px);line-height:1.1;letter-spacing:-.04em;font-weight:700;margin:20px 0;}
.lab-cover p {color:#dce3e9;max-width:640px;}
</style>
'''
def show_cover():
    from IPython.display import Markdown
    display(Markdown("""# Лабораторная работа № 1

## По дисциплине «Прикладная статистика»

**Инфохимики и дизайн**

**Выполнили:**

Иванец Никита Вячеславович — ИСУ **505396**  
Окорокова Елизавета Вадимовна — ИСУ **504843**

**2026**"""))
def apply_style():
    import matplotlib.pyplot as plt
    plt.rcParams.update({'figure.dpi':120,'figure.facecolor':'#faf9f6','axes.facecolor':'#faf9f6',
     'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.titleweight':'bold',
     'axes.labelcolor':'#203343','text.color':'#203343','xtick.color':'#516371','ytick.color':'#516371',
     'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bac5cd',
     'axes.grid':True,'grid.color':'#dce2e5','grid.alpha':.5,'axes.axisbelow':True,
     'axes.prop_cycle':plt.cycler(color=['#345c80','#9b3854','#a48230','#527c6b'])})
