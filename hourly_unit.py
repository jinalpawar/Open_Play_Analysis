import pandas as pd
from bokeh.plotting import figure
from bokeh.layouts import gridplot, column
from bokeh.models import ColumnDataSource, RadioButtonGroup, CustomJS, Range1d, Div
from bokeh.io import curdoc


def hourly_unit(path='hourly_play_processed.csv'):
    hourly = pd.read_csv(path)
    modes = ['All', 'Weekday', 'Weekend']
    dashes = ['solid', 'dashed', 'dotted']
    greys = ['black', 'dimgray', 'darkgray']

    y_max = {}
    for m in modes:
        y_max[m] = float(hourly[hourly['mode'] == m]['value'].max()) * 1.1
    y_range = Range1d(0, y_max['All'])

    sources = []
    plots = []
    for panel in ['platform', 'gender', 'employment', 'care_children']:
        p = figure(title=panel, x_axis_label='Hour (local)', y_axis_label='Minutes per player per day',
                   x_range=(-0.5, 23.5), y_range=y_range,
                   tooltips=[('group', '@group'), ('hour', '@x'), ('minutes', '@y{0.0}')])
        part = hourly[hourly['panel'] == panel]
        k = 0
        for group in part['group'].unique():
            one = part[part['group'] == group]
            data = {'x': list(range(24)), 'group': [group] * 24}
            for m in modes:
                data[m] = one[one['mode'] == m].sort_values('hour')['value'].tolist()
            data['y'] = data['All']# the line shows column y
            source = ColumnDataSource(data)
            sources.append(source)
            n = one['n'].iloc[0]
            p.line('x', 'y', source=source, legend_label=f'{group} (n={n})',
                   line_dash=dashes[k], color=greys[k], line_width=2)
            k += 1
        p.xaxis.ticker = [0, 3, 6, 9, 12, 15, 18, 21]
        p.legend.location = 'top_left'
        p.legend.click_policy = 'hide'
        p.legend.label_text_font_size = '8pt'
        plots.append(p)
    # buttons: when one is clicked, copy that mode's column into y 
    buttons = RadioButtonGroup(labels=modes, active=0)
    buttons.js_on_change('active', CustomJS(
        args=dict(sources=sources, y_range=y_range, modes=modes, y_max=y_max),
        code="""
        const m = modes[cb_obj.active];
        for (const s of sources) {
            s.data.y = s.data[m].slice();
            s.change.emit();
        }
        y_range.end = y_max[m];
        """))

    title = Div(text='<h2>When do people play?</h2>'
                     '<p>Average minutes of play per player, by local hour. '
                     'Weekday / Weekend: an average weekday or weekend day.</p>')
    grid = gridplot(plots, ncols=2, width=600, height=400)
    return column(title, buttons, grid)
if __name__.startswith('bokeh'):
    curdoc().add_root(hourly_unit())