
from bokeh.plotting import figure, curdoc
from bokeh.models import (
    Div,  # HTML div element for custom HTML/CSS content
    Button,  # Interactive button widget - triggers Python callbacks on click
    Slider,  # Numeric slider widget - triggers callbacks on value change
    Select,  # Dropdown selection widget - triggers callbacks on selection
    ColumnDataSource,  # CRITICAL: Bokeh's fundamental data structure
    HoverTool,  # Interactive hover tooltips - shows data on mouse hover
    LinearColorMapper,  # Maps numeric values to colors linearly
    ColorBar,  # Visual legend for color mappers
    BasicTicker,  # Controls tick mark locations on axes
    PrintfTickFormatter,  # Formats tick labels using printf-style strings
)

from bokeh.layouts import (
    column,  # Vertical layout - stacks elements top to bottom
    row,  # Horizontal layout - places elements side by side
    layout,  # Grid layout - accepts nested lists for complex layouts
    # Example: layout([[plot1, plot2], [plot3]]) creates 2 rows
)

from bokeh.palettes import (
    RdYlBu11,  # Red-Yellow-Blue diverging palette with 11 colors
    # Good for showing positive/negative values
    Category20,  # Categorical palette with up to 20 distinct colors
    # Dictionary with keys for different numbers of colors (3,4,5...20)
    Colorblind
)

from bokeh.transform import (
    factor_cmap,  # Maps categorical factors to colors
    # More efficient than manually assigning colors
)

import numpy as np
import pandas as pd
import base64  # For encoding images as base64 strings to embed in HTML
from datetime import date, datetime, timedelta

from demographics import demographics
from wellbeing_vs_playtime import wellbeing_vs_playtime, playtime_spike
from keywords_vs_gender import keywords_vs_gender


class InteractivePresentation:
    """
    Main application class for the Bokeh presentation system.
    """

    def __init__(self):
        self.datasets = {
            "meta" : pd.read_csv('https://github.com/digital-wellbeing/open-play/raw/refs/heads/main/data/clean/game_metadata.csv.gz'),
            "intake" : pd.read_csv("https://github.com/digital-wellbeing/open-play/raw/refs/heads/main/data/clean/survey_intake.csv.gz"),
            "daily" : pd.read_csv("https://github.com/digital-wellbeing/open-play/raw/refs/heads/main/data/clean/survey_daily.csv.gz"),
            "biweekly" : pd.read_csv("https://github.com/digital-wellbeing/open-play/raw/refs/heads/main/data/clean/survey_biweekly.csv.gz"),
            "xbox" : pd.read_csv('https://github.com/digital-wellbeing/open-play/raw/refs/heads/main/data/clean/xbox.csv.gz'),
            "steam" : pd.read_csv("https://github.com/digital-wellbeing/open-play/raw/refs/heads/main/data/clean/steam.csv.gz"),
            "nintendo" : pd.read_csv("https://github.com/digital-wellbeing/open-play/raw/refs/heads/main/data/clean/nintendo.csv.gz")
        }
        self.current_slide = 0  # Track which slide is currently displayed
        self.total_slides = 7  # Total number of slides in presentation
        self.slides = []  # Will hold Bokeh layout objects for each slide
        self.auto_play = False  # Flag for auto-advance mode
        self.auto_play_callback = (None)
        self.create_slides()
        self.create_navigation()
        self.create_layout()

    def create_navigation(self):
        """
        Create navigation controls
        """
        
        self.prev_button = Button(
            label="◀ Previous", button_type="primary", width=100
        )
        self.next_button = Button(
            label="Next ▶", button_type="primary", width=100
        )
        self.home_button = Button(
            label="🏠 Home", button_type="warning", width=100
        )


        slide_options = [
            (str(i), f"Slide {i + 1}: {self.get_slide_title(i)}")
            for i in range(self.total_slides)
        ]
        self.slide_select = Select(
            title="Jump to:",  # Label above dropdown
            value="0",  # Initial selection (must match a value from options)
            options=slide_options,  # List of (value, label) tuples
            width=300,
        )

        self.progress_div = Div(
            text=self.get_progress_html(),  # HTML string
            width=200,  # Width in pixels
        )

        self.prev_button.on_click(self.prev_slide)
        self.next_button.on_click(self.next_slide)
        self.home_button.on_click(self.go_home)
        self.slide_select.on_change("value", self.jump_to_slide)

    def get_slide_title(self, index):
        """Get title for each slide"""
        titles = [
            "The Dataset",
            "Who plays when?",
            "",
            "Does gaming make us unhappy?"
            "When play time spikes (why?), does it affect the wellbeing?",
            "Conclusion"
        ]
        return titles[index] if index < len(titles) else f"Slide {index + 1}"

    def get_progress_html(self):
        """Generate progress bar HTML"""
        progress_pct = ((self.current_slide + 1) / self.total_slides) * 100
        return f"""
        <div style="text-align: center;">
            <b>Slide {self.current_slide + 1} of {self.total_slides}</b><br>
            <div style="width: 100%; background-color: #f0f0f0; border-radius: 5px;">
                <div style="width: {progress_pct}%; background-color: #4CAF50; 
                           height: 20px; border-radius: 5px;"></div>
            </div>
        </div>
        """

    def create_slides(self):
        """Create all presentation slides"""
        self.slides = [
            self.create_slide_1_introduction(),
            self.create_slide_2_demographics(),
            self.create_slide_3_losing_control(),
            self.create_slide_4_playtime_vs_wellbeing(),
            self.create_slide_5_playtime_spikes(),
            self.create_slide_6_conclusions()
        ]

    def create_slide_1_introduction(self):
        """Slide 1: Welcome and Introduction"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            Open Play Dataset (v1.2.6)
        </h1>
        """,
            width=800,  # Fixed width in pixels
            height=80,  # Fixed height in pixels
        )

        # Info panels
        features = Div(
            text="""
        <div style="background-color: #ecf0f1; padding: 20px; border-radius: 10px;">
            <h3>Researchers from University of Oxford, Tilburg University, Karolinska Institute presented a dataset featuring:</h3>
            <ul style="font-size: 14px;">
                <li>Telemetry data from Nintendo, Steam & Microsoft</li>
                <li>12-week survey about mental wellbeing and gaming habits</li>
                <li>~2,000 participants</li>
                <li>1.5M hours of video game play across 10,000+ games</li>
            </ul>
        </div>
        """,
            width=1000,
            height=300,
        )

        # === LAYOUT COMPOSITION ===
        return layout(
            [
                [title],  # Row 1: Title
                [
                    column(features)
                ],  # Row 2: Two columns
            ]
        )

    def create_slide_2_demographics(self):
        """Slide 2:Demographic Exploration"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            Do playtimes differ based on demographic information?
        </h1>

        """,
            width=800,
        )

        return layout(
                    [
                        [title],  # Row 1: Title
                        [
                            column(demographics(**self.datasets))
                        ],  # Row 2: Two columns
                    ]
                )

    def create_slide_3_losing_control(self):
        """Slide 3: Losing control"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            When a player's mental wellbeing is not great, do they feel like you lost control over playtime?
        </h1>

        """,
            width=1200
        )
        gender_keyword = keywords_vs_gender(**self.datasets)
        source = ColumnDataSource(gender_keyword)

        p = figure(width=600, height=400, title="Gender v/s Game Keywords")
        p.hbar_stack(gender_keyword.columns[1:], 
                     y=gender_keyword.columns[0], 
                     height=0.6, 
                     source=source,
                     color=Colorblind[len(gender_keyword.columns[1:])])                        
        p.ygrid.grid_line_color = None

        return layout(
                    [
                        [title],  # Row 1: Title
                        [
                            column(p)
                        ],  # Row 2: Two columns
                    ]
                )

    def create_slide_4_playtime_vs_wellbeing(self):
        """Slide 4: Wellbeing Index v/s Playtime"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            Do players play more when they're doing bad?
        </h1>

        """,
            width=800,
        )

        source = ColumnDataSource(wellbeing_vs_playtime(**self.datasets))

        p = figure(
            width=600, height=400, title="Wellbeing Index v/s Playtime over 2 weeks"
        )

        p.scatter(
            "x",
            "y",  # Position columns (required)
            # color="colors",  # Color column (can be scalar or column name)
            # alpha=0.6,  # Transparency (0=transparent, 1=opaque)
            source=source,  # Data source (ColumnDataSource)
        )

        return layout(
                    [
                        [title],  # Row 1: Title
                        [
                            column(p)
                        ],  # Row 2: Two columns
                    ]
                )

    def create_slide_5_playtime_spikes(self):
        """Slide 5: Wellbeing Index v/s Playtime Spikes"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            When playtimes spike (why?), does the wellbeing index increase too?
        </h1>

        """,
            width=800,
        )
        per_day_2025, per_day_2025_smooth, biweekly_wellbeing, biweekly_wellbeing_smooth = playtime_spike(**self.datasets)

        source_per_day = ColumnDataSource(per_day_2025)
        source_wellbeing = ColumnDataSource(biweekly_wellbeing)

        source_per_day_sm = ColumnDataSource(per_day_2025_smooth)
        source_wellbeing_sm = ColumnDataSource(biweekly_wellbeing_smooth)

        p = figure(
            width=600, height=400, title="Exploring Playtime Spikes and Effect on Wellbeing Index"
        )

        p.line(
            "x",
            "y",  # Position columns (required)
            color="green",  # Color column (can be scalar or column name)
            alpha=0.3,  # Transparency (0=transparent, 1=opaque)
            source=source_per_day,  # Data source (ColumnDataSource)
        )

        p.line(
            "x",
            "y",  # Position columns (required)
            color="red",  # Color column (can be scalar or column name)
            alpha=0.3,  # Transparency (0=transparent, 1=opaque)
            source=source_wellbeing,  # Data source (ColumnDataSource)
        )

        p.line(
                "x",
                "y",  # Position columns (required)
                color="green",  # Color column (can be scalar or column name)
                source=source_per_day_sm,  # Data source (ColumnDataSource)
                legend_label="Avg Per Day"
            )

        p.line(
                "x",
                "y",  # Position columns (required)
                color="red",  # Color column (can be scalar or column name)
                source=source_wellbeing_sm,  # Data source (ColumnDataSource)
                legend_label="Wellbeing Index"

            )

        p.legend.location = 'top_left'

        return layout(
                    [
                        [title],  # Row 1: Title
                        [
                            column(p)
                        ],  # Row 2: Two columns
                    ]
                )

    def create_slide_6_conclusions(self):
        """Slide 6: Conclusion"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            Conclusion
        </h1>
        """,
            width=1000,  # Fixed width in pixels
            height=300,  # Fixed height in pixels
        )

        # Info panels
        features = Div(
            text="""
        <div style="background-color: #ecf0f1; padding: 20px; border-radius: 10px;">
            <h3>While understanding psychological effect of gaming will require more analysis, we can concur that overall people derive value out of this hobby.</h3>
            <h3>Demographic trends stay true to rational beliefs</h3>
            <h3>Gender and other categorical exploration can offer interesting insights</h3>
            <h3>New game releases lead to strong rise in interest and committment</h3>

        </div>
        """,
            width=1000,
            height=300,
        )

        # === LAYOUT COMPOSITION ===
        return layout(
            [
                [title],  # Row 1: Title
                [
                    column(features)
                ],  # Row 2: Two columns
            ]
        )

    def prev_slide(self):
        """Go to previous slide"""
        if self.current_slide > 0:
            self.current_slide -= 1
            self.update_slide()

    def next_slide(self):
        """Go to next slide"""
        if self.current_slide < self.total_slides - 1:
            self.current_slide += 1
            self.update_slide()
        elif self.auto_play:
            # Loop back to beginning in auto-play mode
            self.current_slide = 0
            self.update_slide()

    def go_home(self):
        """Go to first slide"""
        self.current_slide = 0
        self.update_slide()

    def jump_to_slide(self, attr, old, new):
        """Jump to specific slide"""
        self.current_slide = int(new)
        self.update_slide()

    def create_layout(self):
        """Create the main layout"""

        # === NAVIGATION BAR ===
        # row() places all navigation elements horizontally
        nav_bar = row(
            self.prev_button,
            self.home_button,
            self.next_button,
            self.slide_select,
            self.progress_div,
        )

        # === MAIN CONTENT AREA ===
        self.main_content = column(self.slides[0])

        # === FULL APPLICATION LAYOUT ===
        self.layout = column(
            nav_bar,  # Navigation controls
            Div(text="<hr>", width=1200, height=10),  # Visual separator
            self.main_content,  # Slide content
        )

        # Initialize display with first slide
        self.update_slide()

    def update_slide(self):
        """Update the current slide display

        === CENTRAL UPDATE PATTERN ===
        This method is called whenever slide changes.
        Updates all UI elements to reflect new state.
        """

        # === WIDGET STATE MANAGEMENT ===
        # Disable navigation buttons at boundaries
        # Setting .disabled property grays out button and prevents clicks
        self.prev_button.disabled = self.current_slide == 0
        self.next_button.disabled = self.current_slide == self.total_slides - 1

        # === UPDATING DIV CONTENT ===
        # Changing .text property updates HTML content
        # Bokeh automatically syncs to browser
        self.progress_div.text = self.get_progress_html()

        # === UPDATING SELECT WIDGET ===
        # Setting .value changes selection
        # Must be string matching one of the option values
        self.slide_select.value = str(self.current_slide)

        # === UPDATING LAYOUT CHILDREN ===
        # CRITICAL: This is how to swap content in Bokeh!
        # Layout.children is a list of child elements
        # Replacing the list changes what's displayed
        # Bokeh handles all DOM updates automatically
        self.main_content.children = [self.slides[self.current_slide]]

        # Server-side logging (appears in terminal, not browser)
        print(
            f"Showing slide {self.current_slide + 1}: {self.get_slide_title(self.current_slide)}"
        )

presentation = InteractivePresentation()

curdoc().add_root(presentation.layout)
curdoc().title = "Open Play Analysis"

# Server Side logging
print("=" * 50)
print("Interactive Presentation App Started!")
print("=" * 50)
print("Navigate through slides using controls")
print("All visualizations are interactive")
print("Try Auto Play for presentation mode")
print("=" * 50)

