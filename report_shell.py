"""Add the report's reading interface without changing scientific outputs."""
from pathlib import Path
from html import escape
import re
from bs4 import BeautifulSoup

COLAB='https://colab.research.google.com/drive/1t0ezoYShehzp7R8UtJfTTSB9LwQY3_rT?usp=sharing'

def decorate_report(html, notebook, root):
    root=Path(root)
    soup=BeautifulSoup(html,'html.parser')
    if soup.select_one('.report-shell'):
        raise ValueError('Интерфейс отчёта уже добавлен')
    soup.html['lang']='ru'
    soup.title.string='Лабораторная работа №1 · Прикладная статистика'
    for meta in soup.head.find_all('meta', attrs={'name':'viewport'}):meta.decompose()
    viewport=soup.new_tag('meta',attrs={'name':'viewport','content':'width=device-width, initial-scale=1'})
    soup.head.append(viewport)
    style=soup.new_tag('style',id='report-interface-style');style.string=(root/'report_ui.css').read_text();soup.head.append(style)
    main=soup.body.find('main',recursive=False)
    if main is None:raise ValueError('Не найден документ отчёта')
    main['class']=['report-main'];main['id']='report-main'
    document=soup.new_tag('div',attrs={'class':'report-document'})
    for child in list(main.contents):document.append(child.extract())
    nav=[]
    for c in notebook.cells:
        if c.cell_type!='markdown':continue
        match=re.search(r'^#{1,6} (\d+(?:\.\d+)*) · (.+)$',c.source,re.M)
        if not match:continue
        num,title=match.groups();cell_id=c.metadata['id'];depth=min(3,num.count('.')+1)
        nav.append(f'<a href="#lab-cell-{escape(cell_id)}" data-cell="cell-id={escape(cell_id)}" data-depth="{depth}"><span class="report-nav-num">{escape(num)}</span><span>{escape(title)}</span></a>')
    count=sum('mountLab(document.getElementById(' in str(o.get('data',{}).get('text/html','')) for c in notebook.cells if c.cell_type=='code' for o in c.get('outputs',[]))
    frame=f'''<div class="report-shell" id="report-top">
<a class="report-skip" href="#report-main">К содержанию исследования</a>
<button class="report-backdrop" aria-label="Закрыть меню разделов" type="button"></button>
<aside class="report-sidebar" aria-label="Навигация по лабораторной">
<a class="report-brand" href="#report-top"><span class="report-monogram">01</span><span><b>ПРИКЛАДНАЯ<br>СТАТИСТИКА</b><small>ИТМО · Лабораторная работа</small></span></a>
<div class="report-nav-label">Содержание исследования</div>
<div class="report-search"><label for="report-search" hidden>Найти раздел</label><input id="report-search" type="search" placeholder="Найти раздел…" autocomplete="off"><button class="report-clear" type="button" aria-label="Очистить поиск" hidden>×</button></div>
<button class="report-subtoggle" type="button" aria-expanded="false">Показать все подразделы</button>
<nav class="report-nav" aria-label="Разделы отчёта">{''.join(nav)}<p class="report-nav-empty" hidden>Раздел не найден</p></nav>
<div class="report-sidebar-foot"><span>ИНФОХИМИКИ И ДИЗАЙНЕРЫ</span><span>2026</span></div>
</aside>
<div class="report-workspace">
<header class="report-topbar"><button class="report-menu" type="button" aria-expanded="false" aria-label="Открыть меню разделов">☰</button><div class="report-topbar-label"><b>LAB 01</b> &nbsp; / &nbsp; Инфохимики и дизайнеры</div><div class="report-topbar-actions"><a href="#lab-cell-a214e921">Оглавление</a><a class="report-open-colab" href="{COLAB}" target="_blank" rel="noopener">Открыть в Colab →</a></div><div class="report-progress" aria-hidden="true"></div></header>
</div></div>'''
    shell=BeautifulSoup(frame,'html.parser').find('div',class_='report-shell')
    hero=f'''<section class="report-hero" aria-labelledby="report-title"><div class="report-hero-top"><div><p class="report-kicker">Лабораторная работа № 1 · 2026</p><h1 id="report-title">Прикладная<br>статистика.</h1><p class="report-hero-desc">Распределения, связи и генерация случайных величин на данных о вине и бриллиантах.</p><div class="report-hero-buttons"><a class="report-button" href="#lab-cell-HyzznKE5OuoI">К исследованию <span aria-hidden="true">↓</span></a><a class="report-button secondary" href="#lab-cell-ttHxBvi5PUR6">К генератору <span aria-hidden="true">→</span></a></div></div><div class="report-datasets"><div class="report-dataset"><small><span class="report-dot"></span>01 / Инфохимия</small><strong>Wine Quality</strong><p>6 497 образцов · pH, сахар, этанол</p></div><a class="report-dataset diamonds" href="#lab-cell-b8QeM286Pmyw" style="text-decoration:none;color:inherit"><small><span class="report-dot"></span>02 / КТвД</small><strong>Diamonds →</strong><p>53 940 записей · масса и цена</p></a></div></div><div class="report-authors"><div class="report-author"><small>КТвД · структура, визуализация и интерактивность</small><strong>Иванец Никита Вячеславович</strong><span>ИСУ 505396</span></div><div class="report-author"><small>Инфохимия · исходное исследование вина</small><strong>Окорокова Елизавета Вадимовна</strong><span>ИСУ 504843</span></div></div><div class="report-statstrip"><div><strong>02</strong><span>датасета</span></div><div><strong>05</strong><span>случайных величин</span></div><div><strong>{count:02}</strong><span>интерактивные панели</span></div></div></section>'''
    main.append(BeautifulSoup(hero,'html.parser'))
    main.append(document)
    for p in document.select('.jp-RenderedMarkdown p'):
        if not p.get_text(strip=True) and p.find('a',id=True):p['class']=p.get('class',[])+['report-anchor-only']
    cover=document.find(id='cell-id=bee525f6')
    if cover:cover['class']=cover.get('class',[])+['report-source-cover']
    for cell_id,label,cls in [('EXDs7hxgiL0M','Подготовка файлов проекта','report-environment'),('2330c410','Среда выполнения и версии библиотек','report-environment'),('a214e921',f'Полное оглавление · {len(nav)} разделов','report-contents')]:
        cell=document.find(id='cell-id='+cell_id)
        if cell:
            details=soup.new_tag('details',attrs={'class':cls});summary=soup.new_tag('summary');summary.string=label;details.append(summary);cell.wrap(details)
    footer=BeautifulSoup('<footer class="report-footer"><span>Лабораторная работа № 1 · Прикладная статистика · 2026</span><span>Графики работают офлайн. Для формул нужен интернет.</span></footer>','html.parser')
    main.append(footer)
    shell.find('div',class_='report-workspace').append(main.extract())
    top=soup.new_tag('a',href='#report-top',attrs={'class':'report-top-link','aria-label':'В начало отчёта'});top.string='↑';shell.append(top)
    soup.body.append(shell)
    script=soup.new_tag('script',id='report-interface-script');script.string=(root/'report_ui.js').read_text();soup.body.append(script)
    return str(soup)
