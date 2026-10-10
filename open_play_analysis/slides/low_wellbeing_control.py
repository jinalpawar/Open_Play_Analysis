from bokeh.models import ColumnDataSource, HoverTool, Label
from bokeh.plotting import figure
import pandas as pd

def as_hours(minutes):
    minutes = int(round(minutes))
    return f"{minutes // 60} h {minutes % 60:02d}"

def create_low_wellbeing_control_grid(path="results_islamia.csv"):

    results = pd.read_csv(path)
    BLUE, EMPTY, INK, MUTED = "#0D2152", "#e4e3df", "#0b0b0b", "#52514e"

    top = {"x": [], "y": [], "color": [], "group": [], "pct": [], "low": [], "players": []}
    bottom = {"x": [], "y": [], "color": [], "group": [], "time": [], "n": []}
    for k, row in results.iterrows():
        x0 = k * 13
        pct = int(round(row["pct_low_wellbeing"]))
        for i in range(100):
            r, c = divmod(i, 10)
            top["x"].append(x0 + c + 0.42); top["y"].append(8.5 - r + 0.42)
            top["color"].append(BLUE if i < pct else EMPTY)
            top["group"].append(row["group"]); top["pct"].append(pct)
            top["low"].append(int(row["low_wellbeing_players"])); top["players"].append(int(row["players"]))
        hours = row["minutes_per_day_low"] / 60
        for h in range(24):
            r, c = divmod(h, 6)
            bottom["x"].append(x0 + 2.75 + c * 0.75 + 0.33); bottom["y"].append(-10.5 - r * 0.75 + 0.33)
            bottom["color"].append(BLUE if hours - h >= 0.5 else EMPTY)     # square coloured if at least half filled
            bottom["group"].append(row["group"]); bottom["time"].append(as_hours(row["minutes_per_day_low"]))
            bottom["n"].append(int(row["low_with_console_data"]))
    
    p = figure(width=950, height=650, x_range=(-0.5, 52), y_range=(-17, 12), match_aspect=True,
            toolbar_location=None,
            title="Wellbeing Index, Loss of Control and Playtime - how are they related?")
    top_glyph = p.rect("x", "y", width=0.85, height=0.85, color="color", source=ColumnDataSource(top))
    bottom_glyph = p.rect("x", "y", width=0.65, height=0.65, color="color", source=ColumnDataSource(bottom))
    p.add_tools(HoverTool(renderers=[top_glyph], tooltips=[
        ("Lose control", "@group"), ("Low wellbeing", "@pct% of them (@low of @players players)")]))
    p.add_tools(HoverTool(renderers=[bottom_glyph], tooltips=[
        ("Lose control", "@group"), ("Average gaming time", "@time a day (@n players with low wellbeing)")]))
    
    for k, row in results.iterrows():
        x0 = k * 13
        pct = int(round(row["pct_low_wellbeing"]))
        p.add_layout(Label(x=x0 + 5, y=-1.4, text=f"Lose control: {row['group']}", text_align="center",
                        text_font_size="12px", text_font_style="bold", text_color=INK))
        p.add_layout(Label(x=x0 + 5, y=-3.2, text=f"→ {pct}% of them have low wellbeing", text_align="center",
                        text_font_size="12px", text_font_style="bold", text_color=BLUE))
        p.add_layout(Label(x=x0 + 5, y=-14.6, text=as_hours(row["minutes_per_day_low"]) + " a day",
                        text_align="center", text_font_size="13px", text_font_style="bold", text_color=BLUE))
    p.add_layout(Label(x=-0.5, y=10.0, text="Each grid = 100 players who gave the same answer. "
                    "Blue = players with low wellbeing (index below 5 out of 10).",
                    text_font_size="13px", text_font_style="bold", text_color=INK))
    p.add_layout(Label(x=-0.5, y=-7.6, text="Average gaming time per day of the blue players above (1 square = 1 hour)",
                    text_font_size="11px", text_color=MUTED))
    
    p.axis.visible = False
    p.grid.visible = False
    p.outline_line_color = None

    return (p)