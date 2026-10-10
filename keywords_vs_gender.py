import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure


def keywords_vs_gender(path="keywords_gender.csv"):

    gender_keyword_wo_0_3 = pd.read_csv(path)
    
    keyword_exp = ["male protagonist", "female protagonist", "magic"] # top 3 themes
    gender = ["Man", "Woman", "Non-binary"]

    from bokeh.palettes import Spectral3
    source = ColumnDataSource(gender_keyword_wo_0_3)

    fig = figure(y_range=gender,
                height=500,
                title="Gender-wise preference of popular game themes",
                x_range=[0,1],
                )

    fig.hbar_stack(keyword_exp,
                y='gender',
                source=source,
                height=0.5,
                color = Spectral3,
                legend_label=keyword_exp)

    # Display Stack Graph
    fig.legend.orientation = "horizontal"
    fig.legend.location = "bottom"

    return fig