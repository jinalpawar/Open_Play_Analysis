import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.palettes import Spectral3

def keywords_vs_gender(path="keywords_gender.csv"):

    gender_keyword_wo_0_3 = pd.read_csv(path)
    
    keyword_exp = ["male_protagonist", "female_protagonist", "magic"]
    gender = ["Man", "Woman", "Non-binary"]

    source = ColumnDataSource(gender_keyword_wo_0_3)

    fig = figure(y_range=gender,
                height=500,
                title="Gender-wise preference of popular game themes",
                x_range=[0,100],
                tooltips=[("Male Protagonist %", "@male_protagonist"), ("Female Protagonist %", "@female_protagonist"), ("Magic %", "@magic")]
                )

    fig.hbar_stack(keyword_exp,
                y='gender',
                source=source,
                height=0.5,
                color = ["#0D2152", "#E0C99C", "#9DCEE4"],
                legend_label=keyword_exp)

    # Display Stack Graph
    fig.legend.orientation = "horizontal"
    fig.legend.location = "bottom"

    return fig