import pandas as pd
from datetime import date
from bokeh.models import ColumnDataSource, LinearAxis, Range1d
from bokeh.plotting import figure

def create_playtime_spikes_wellbeing_graph(path=["per_day_2025.csv", "biweekly_wellbeing.csv"]):

    per_day_2025 = pd.read_csv(path[0], parse_dates=["date"])
    biweekly_wellbeing = pd.read_csv(path[1], parse_dates=["date"])

    source_per_day = ColumnDataSource(per_day_2025)
    source_wellbeing = ColumnDataSource(biweekly_wellbeing)

    p = figure(
        width=950, height=650, title="Exploring Playtime Spikes and Effect on Wellbeing Index", x_axis_type="datetime",
        x_axis_label="Telemetry Timespan",
        y_axis_label="Total playtime per day (in hours)",
        tooltips=[("Total Playtime", "@duration"), ("Average Wellbeing Index", "@wellbeing_index")]
    )
    p.border_fill_color = "#FAF8F2"
    p.background_fill_color = "#FAF8F2"

    p.extra_y_ranges = {"wellbeing_index_scale": Range1d(start=1, end=10)}
    p.add_layout(LinearAxis(y_range_name="wellbeing_index_scale"), 'right')

    p.line(
        "date",
        "duration",  # Position columns (required)
        color="#0D2152",  # Color column (can be scalar or column name)
        alpha=0.3,  # Transparency (0=transparent, 1=opaque)
        source=source_per_day,  # Data source (ColumnDataSource)
    )

    p.line(
        "date",
        "duration_smooth",  # Position columns (required)
        color="#0D2152",  # Color column (can be scalar or column name)
        alpha=0.8,
        line_width=1.5,
        source=source_per_day,  # Data source (ColumnDataSource)
        legend_label="Total Duration"
    )

    p.line(
        "date",
        "wellbeing_index_smooth",  # Position columns (required)
        color="#9DCEE4",  # Color column (can be scalar or column name)
        alpha=0.8,  # Transparency (0=transparent, 1=opaque)
        source=source_wellbeing,  # Data source (ColumnDataSource)
        line_width=1.5,
        legend_label="Wellbeing Index",
        y_range_name="wellbeing_index_scale"
        )

    p.line(
        "date",
        "wellbeing_index",  # Position columns (required)
        color="#9DCEE4",  # Color column (can be scalar or column name)
        source=source_wellbeing,  # Data source (ColumnDataSource)
        alpha=0.3,
        y_range_name="wellbeing_index_scale"

        )

    p.vspan(x=date(2025, 5, 30), color="#6E40CF", legend_label="Observed Spikes", line_width=1.5)
    p.vspan(x=date(2025, 2, 27), color="#6E40CF", line_width=1.5)

    p.legend.location = "top_left"

    return p