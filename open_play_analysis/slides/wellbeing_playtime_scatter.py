import pandas as pd
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.models import ColumnDataSource

def wellbeing_playtime_scatter(path="per_pid_2weeks.csv"):
    per_pid_2weeks = pd.read_csv(path)

    colors = ["#0D2152", "#E0C99C", "#9DCEE4"]

    neuro_status =  sorted(per_pid_2weeks.neuro_status.unique())
    data = ColumnDataSource(per_pid_2weeks)
    
    p = figure(title = "Wellness v/s Playtime", width=950, height=650, tooltips=[("Playtime", "@playtime_2weeks_hrs"), ("Wellbeing Index", "@wellbeing_index"), ("Diagnosed", "@neuro_status")])
    
    p.xaxis.axis_label = 'Wellness Index'
    p.yaxis.axis_label = 'Avg Playtime per 2 weeks (in hours)'
    p.border_fill_color = "#FAF8F2"
    p.background_fill_color = "#FAF8F2"

    p.scatter("wellbeing_index", "playtime_2weeks_hrs", source=data,
            legend_group="neuro_status", fill_alpha=0.3, size=12,
            color=factor_cmap('neuro_status', colors, neuro_status))

    p.legend.location = "top_left"
    p.legend.title = "Neuro-divergence Diagnosed"

    return p

