import marimo
__generated_with = "0.25.2"
app = marimo.App(width="full", app_title="Лабораторная работа №1")

@app.cell(hide_code=True)
def _():
    import marimo as mo
    from interactive_context import load_context
    from lab_interactive import payload, iframe_html
    return mo, load_context, payload, iframe_html

@app.cell(hide_code=True)
def _(load_context):
    context = load_context()
    return (context,)

@app.cell(hide_code=True)
def _(mo):
    sections = {
        'Аудит вина':'audit', 'Разбиение train / holdout':'split',
        'Вино: EDA':'eda', 'Модели распределений':'models',
        'Нормальность pH':'normality', 'Связи показателей вина':'pairs',
        'Различие средних (Welch)':'welch', 'Нормализация':'scale',
        'Случайные выборки':'sample', 'Состоятельность оценок':'consistency',
        'Генератор pH':'generator', 'Диагностика DKW':'diagnostics',
        'Holdout и автокорреляция':'holdout', 'Замер скорости':'speed',
        'Восемь алгоритмов':'gallery', 'Бриллианты: EDA':'diamonds',
        'Цена при фиксированной массе':'mass', 'Масса и цена: связь':'diamond_pair'
    }
    section=mo.ui.dropdown(sections, value='Вино: EDA', label='Раздел исследования')
    mo.vstack([mo.md('# Лабораторная работа №1\nИнфохимики и дизайнеры · Прикладная статистика · 2026\n\nИванец Никита Вячеславович · ИСУ 505396  \nОкорокова Елизавета Вадимовна · ИСУ 504843'),section])
    return (section,)

@app.cell(hide_code=True)
def _(mo, section, context, payload, iframe_html):
    mo.Html(iframe_html(payload(section.value, context)))
    return

if __name__ == '__main__':
    app.run()
