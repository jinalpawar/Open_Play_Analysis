from bokeh.plotting import curdoc
from bokeh.plotting import output_file
from bokeh.models import (
    Div,  # HTML div element for custom HTML/CSS content
    Button,
    GlobalImportedStyleSheet,
    ImportedStyleSheet,
    Select,  # Dropdown selection widget - triggers callbacks on selection
)

from bokeh.layouts import (
    column,  # Vertical layout - stacks elements top to bottom
    row,  # Horizontal layout - places elements side by side
    layout,  # Grid layout - accepts nested lists for complex layouts
    # Example: layout([[plot1, plot2], [plot3]]) creates 2 rows
)


from slides.hourly_unit import hourly_unit
from slides.wellbeing_vs_playtime_graph import create_playtime_spikes_wellbeing_graph
from slides.keywords_vs_gender import keywords_vs_gender
from slides.low_wellbeing_control import create_low_wellbeing_control_grid
from slides.wellbeing_playtime_scatter import wellbeing_playtime_scatter

class InteractivePresentation:
    """
    Main application class for the Bokeh presentation system.
    """

    def __init__(self):
        self.current_slide = 0  # Track which slide is currently displayed
        self.total_slides = 7  # Total number of slides in presentation
        self.slides = []  # Will hold Bokeh layout objects for each slide
        self.auto_play = False  # Flag for auto-advance mode
        self.auto_play_callback = (None)
        self.style = ImportedStyleSheet(url="open_play_analysis/static/styles.css")
        self.global_style = GlobalImportedStyleSheet(url="open_play_analysis/static/global.css")
        self.create_slides()
        self.create_navigation()
        self.create_layout()

    def create_navigation(self):
        """
        Create navigation controls
        """

        self.prev_button = Button(
            label="◀ Previous", stylesheets=[self.style, self.global_style]
        )
        self.next_button = Button(
            label="Next ▶", stylesheets=[self.style]
        )
        self.home_button = Button(
            label="🏠 Home", stylesheets=[self.style]
        )

        self.prev_button.on_click(self.prev_slide)
        self.next_button.on_click(self.next_slide)
        self.home_button.on_click(self.go_home)

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
        self.slide_select.on_change("value", self.jump_to_slide)

    def get_slide_title(self, index):
        """Get title for each slide"""
        titles = [
            "The Dataset",
            "Who plays when?",
            "Spikes, Rings & Runes",
            "Loss of Control, Wellbeing Index and Playtime",
            "Gender-wise Game Theme Preferences",
            "Neuro-divergence, Wellbeing and Playtime",
            "Final Thoughts"
        ]
        return titles[index] if index < len(titles) else f"Slide {index + 1}"

    def create_slides(self):
        """Create all presentation slides"""
        self.slides = [
            self.create_slide_1(),
            self.create_slide_2(),
            self.create_slide_3(),
            self.create_slide_4(),
            self.create_slide_5(),
            self.create_slide_6(),
            self.create_slide_7()
        ]

    def create_slide_1(self):
        """Welcome and Introduction"""

        title = Div(
            text="""
            <div style="
                background: #0D2152;
                border: 3px solid #C5CFDC;
                border-radius: 20px;
                padding: 30px 32px 20px 32px;
                margin: 18px 0;
                width: 950px;
                max-width: 950px;
                font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
            ">
                <h3 style="
                    color: #FFF9E6;
                    font-size: 1.8em; font-weight: bold;
                    margin-top: 0; margin-bottom: 10px;
                    letter-spacing: 1px;
                    text-shadow: 0 2px 20px #f59e0b55;
                    @font-face {
                        font-family: "Press Start 2P";
                        src: url("PressStart2P-Regular.ttf") format("ttf"),
                        };
                ">
                     🎮 Open Play Dataset (v1.2.6)
                </h3>
            """
        )

        description = Div(
        text="""
        <div style="
            background: #0D2152;
            border: 3px solid #C5CFDC;
            border-radius: 20px;
            padding: 30px 32px 20px 32px;
            margin: 18px 0;
            width:100%;
            width: 950px;
            max-width: 950px;
            font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
        ">
            <h3 style="
                color: #F4F2ED;
                font-size: 1.8em; font-weight: bold;
                margin-top: 0; margin-bottom: 10px;
                letter-spacing: 1px;
                text-shadow: 0 2px 20px #f59e0b55;,
                }
            ">
                Analyzing Gaming habits and mental wellbeing amongst adults aged between 18-40 years
            </h3>

            <h4 style="
                color: #F4F2ED;
                font-size: 1.5em; font-weight: bold;
                margin-top: 0; margin-bottom: 10px;
                letter-spacing: 1px;
                text-shadow: 0 2px 20px #f59e0b55;,
                }
            ">
                Dataset created by Researchers from University of Oxford, Tilburg University, Karolinska Institute
            </h4>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 20px;">
                <div>
                    <h4 style="color: #F4F2ED; font-size: 1.5em; margin-bottom: 10px;">📋 Dataset Details</h4>
                    <ul style="color: #F4F2ED; font-size: 1.3em; padding-left: 17px; margin-top: 0;">
                        <li>Telemetry data from Nintendo, Steam & Microsoft across 43 months (2022-2025) </li>
                        <li>12-week survey about mental wellbeing and gaming habits</li>
                        <li>~4,000 participants combined from US & UK</li>
                        <li>1.5M hours of video game play across 10,000+ games</li>
                    </ul>
                </div>
                <div>
                    <h4 style="color: #F4F2ED; font-size: 1.5em; margin-bottom: 10px;">⚙️ Dataset Features</h4>
                    <ul style="color: #F4F2ED; font-size: 1.3em; padding-left: 17px; margin-top: 0;">
                        <li><strong>Gaming session logs across platforms</strong></li>
                        <li><strong>Game Metadata</strong></li>
                        <li><strong>Survey questions about depressive symptoms, satisfaction with life, gaming attitude</strong></li>
                        <li><strong>Demographic details</strong></li>
                    </ul>
                </div>
            </div>
        </div>
        """,
        width=650, height=410
        )

        # === LAYOUT COMPOSITION ===
        return layout(
            [
                [title],
                [column(description)]
            ]
        )

    def create_slide_2(self):
        """Demographic Exploration"""

        title = Div(
            text="""
            <div style="
                background: #0D2152;
                border: 3px solid #C5CFDC;
                border-radius: 20px;
                padding: 30px 5px 20px 32px;
                margin: 18px 0;
                width: 950px;
                max-width: 950px;
                font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
            ">
                <h3 style="
                    color: #FFF9E6;
                    font-size: 1.8em; font-weight: bold;
                    margin-top: 0; margin-bottom: 10px;
                    letter-spacing: 1px;
                    text-shadow: 0 2px 20px #f59e0b55;
                    @font-face {
                        font-family: "Press Start 2P";
                        src: url("PressStart2P-Regular.ttf") format("ttf"),
                        };
                ">
                     Do playtimes differ based on demographics?
                </h3>
            """
        )

        observations = Div(
        text="""
        <div style="
            background: #0D2152;
            border: 3px solid #C5CFDC;
            border-radius: 20px;
            padding: 30px 32px 20px 32px;
            margin: 18px 0;
            width: 950px;
            max-width: 950px;
            font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
        ">

            <h4 style="color: #F4F2ED; font-size: 1.5em; margin-bottom: 10px; margin-top: 0;">Observations</h4>
            <ul style="color: #F4F2ED; font-size: 1.3em; padding-left: 17px; margin-top: 0;">
                <li><strong>Noticeable difference between weekend and weekday playtimes across demographics</strong></li>
                <li><strong>As expected, playtimes peak during evening period across demographics</strong></li>
                <li><strong>Nintendo playtime is comparatively lower than other platforms</strong></li>
                <li><strong>Gender-wise distribution shows female participants tended to play for shorter periods during same timeframes</strong></li>
                <li><strong>While student and full-time employed participants share mostly same distribution with slight deviations, unemployed participants play for longer than both and for a larger timeframe.</strong></li>
                <li><strong>Participants who care for children display a short dip between 16 to 18, which could be attribtued to childcare-related activities</strong></li>
            </ul>
        </div>
        """,
        width=650, height=410
        )

        return layout(
                    [
                        [title],  # Row 1: Title
                        [hourly_unit()],  # Row 2: Two columns
                        [observations],
                    ]
                )

    def create_slide_3(self):
        """Playtime Spikes & Wellbeing Index"""

        title = Div(
            text="""
            <div style="
                background: #0D2152;
                border: 3px solid #C5CFDC;
                border-radius: 20px;
                padding: 30px 5px 20px 32px;
                margin: 18px 0;
                width: 950px;
                max-width: 950px;
                font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
            ">
                <h3 style="
                    color: #FFF9E6;
                    font-size: 1.8em; font-weight: bold;
                    margin-top: 0; margin-bottom: 10px;
                    letter-spacing: 1px;
                    text-shadow: 0 2px 20px #f59e0b55;
                    @font-face {
                        font-family: "Press Start 2P";
                        src: url("PressStart2P-Regular.ttf") format("ttf"),
                        };
                ">
                      When playtimes spike (why?), does the wellbeing index increase too?
                </h3>
            """
        )

        wellbeing_idx_desc = Div(
        text="""
        <div style="
            background: #0D2152;
            border: 3px solid #C5CFDC;
            border-radius: 20px;
            padding: 30px 32px 20px 32px;
            margin: 18px 0;
            width: 950px;
            max-width: 950px;
            font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
        ">

        <h4 style="color: #F4F2ED; font-size: 1.5em; margin-bottom: 10px; margin-top: 0;">Wellbeing Index</h4>
        <ul style="color: #F4F2ED; font-size: 1.3em; padding-left: 17px; margin-top: 0;">
            <li>Wellbeing Index is a composite index built on survey responses for PROMIS Measure, Warwick-Edinburgh Mental Wellbeing Scale and Cantril Self-anchoring Scale </li>
            <li>The scale ranges from 0 to 10, with higher value representing higher happiness/satisfaction with life</li>
        </ul>
        </div>
        """,
        width=650, height=200
        )

        observations = Div(
        text="""
        <div style="
            background: #0D2152;
            border: 3px solid #C5CFDC;
            border-radius: 20px;
            padding: 30px 32px 20px 32px;
            margin: 18px 0;
            width: 950px;
            max-width: 950px;
            font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
        ">

            <h4 style="color: #F4F2ED; font-size: 1.5em; margin-bottom: 10px; margin-top: 0;">Observations</h4>
            <ul style="color: #F4F2ED; font-size: 1.3em; padding-left: 17px; margin-top: 0;">
                <li><strong>Two large spikes can be observed at 2 points in time: end of February 2025, & start of June 2025. These dates coincide with the release of popular games such as R.E.P.O., Monster High Wilds in last week of Feb 2025 and Elden Ring, Deltarune in first week of June 2025 </strong></li>
                <li><strong>Thus, release of highly anticipated games lead to surge in playtime</strong></li>
                <li><strong>This spike coincides with a strong and later a weak/almost inconsiderable surge in wellbeing-index.</strong></li>
                <li><strong>If we look at underneath to real values, we observe large fluctuations in wellbeing index. This could indicate that some participants may have regretted their playtime spikes.</strong></li>
            </ul>
        </div>
        """,
        width=650, height=410
        )


        return layout(
                    [
                        [title],  # Row 1: Title
                        [column(create_playtime_spikes_wellbeing_graph())],  # Row 2: Two columns
                        [wellbeing_idx_desc],
                        [observations],
                    ]
                )

    def create_slide_4(self):
        """How does gaming affect our sense of control?"""

        title = Div(
            text="""
            <div style="
                background: #0D2152;
                border: 3px solid #C5CFDC;
                border-radius: 20px;
                padding: 30px 5px 20px 32px;
                margin: 18px 0;
                width: 950px;
                max-width: 950px;
                width:100%;
                font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
            ">
                <h3 style="
                    color: #FFF9E6;
                    font-size: 1.8em; font-weight: bold;
                    margin-top: 0; margin-bottom: 10px;
                    letter-spacing: 1px;
                    text-shadow: 0 2px 20px #f59e0b55;
                    @font-face {
                        font-family: "Press Start 2P";
                        src: url("PressStart2P-Regular.ttf") format("ttf"),
                        };
                ">
                    The relationship between wellbeing index and loss of control of gaming time
                </h3>
            """
        )

        observations = Div(
        text="""
        <div style="
            background: #0D2152;
            border: 3px solid #C5CFDC;
            border-radius: 20px;
            padding: 30px 32px 20px 32px;
            margin: 18px 0;
            width: 950px;
            max-width: 950px;
            font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
        ">

            <h4 style="color: #F4F2ED; font-size: 1.5em; margin-bottom: 10px; margin-top: 0;">Observations</h4>
            <ul style="color: #F4F2ED; font-size: 1.3em; padding-left: 17px; margin-top: 0;">
                <li><strong>The more players lose control, the more often they have low wellbeing and the longer these players spend gaming each day </strong></li>
            </ul>
        </div>
        """,
        width=650, height=410
        )

        return layout(
                    [
                        [title],  # Row 1: Title
                        [column(create_low_wellbeing_control_grid())],
                        [observations],
                    ]
                )

    def create_slide_5(self):
        """Gender-wise Preferences"""

        title = Div(
            text="""
            <div style="
                background: #0D2152;
                border: 3px solid #C5CFDC;
                border-radius: 20px;
                padding: 30px 5px 20px 32px;
                margin: 18px 0;
                width: 950px;
                max-width: 950px;
                font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
            ">
                <h3 style="
                    color: #FFF9E6;
                    font-size: 1.8em; font-weight: bold;
                    margin-top: 0; margin-bottom: 10px;
                    letter-spacing: 1px;
                    text-shadow: 0 2px 20px #f59e0b55;
                    @font-face {
                        font-family: "Press Start 2P";
                        src: url("PressStart2P-Regular.ttf") format("ttf"),
                        };
                ">
                    Do people of a gender, game together?
                </h3>
            """
        )

        observations = Div(
        text="""
        <div style="
            background: #0D2152;
            border: 3px solid #C5CFDC;
            border-radius: 20px;
            padding: 30px 32px 20px 32px;
            margin: 18px 0;
            width: 950px;
            max-width: 950px;
            font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
        ">

            <h4 style="color: #F4F2ED; font-size: 1.5em; margin-bottom: 10px; margin-top: 0;">Observations</h4>
            <ul style="color: #F4F2ED; font-size: 1.3em; padding-left: 17px; margin-top: 0;">
                <li><strong>No specific gender displays an overwhelmingly strong preference for a theme</strong></li>
                <li><strong>Participants with "Male" (or equivalent) identities play magic-themed games higher than other particpants</strong></li>
                <li><strong>Surprisingly, participants with Female (or equivalent) identities play with male protagonists games higher than other particpants</strong></li>
            </ul>
        </div>
        """,
        width=650, height=410
        )


        return layout(
                    [
                        [title],  # Row 1: Title
                        [column(keywords_vs_gender())],  # Row 2: Two columns
                        [observations]
                    ]
                )

    def create_slide_6(self):
        """Wellbeing Playtime Scatter"""

        title = Div(
            text="""
            <div style="
                background: #0D2152;
                border: 3px solid #C5CFDC;
                border-radius: 20px;
                padding: 30px 5px 20px 32px;
                margin: 18px 0;
                width: 950px;
                max-width: 950px;
                font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
            ">
                <h3 style="
                    color: #FFF9E6;
                    font-size: 1.8em; font-weight: bold;
                    margin-top: 0; margin-bottom: 10px;
                    letter-spacing: 1px;
                    text-shadow: 0 2px 20px #f59e0b55;
                    @font-face {
                        font-family: "Press Start 2P";
                        src: url("PressStart2P-Regular.ttf") format("ttf"),
                        };
                ">
                    Does Neuro-divergence play a role in playtime and wellbeing?
                </h3>
            """
        )

        observations = Div(
        text="""
        <div style="
            background: #0D2152;
            border: 3px solid #C5CFDC;
            border-radius: 20px;
            padding: 30px 32px 20px 32px;
            margin: 18px 0;
            width: 950px;
            max-width: 950px;
            font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
        ">

            <h4 style="color: #F4F2ED; font-size: 1.5em; margin-bottom: 10px; margin-top: 0;">Observations</h4>
            <ul style="color: #F4F2ED; font-size: 1.3em; padding-left: 17px; margin-top: 0;">
                <li><strong>Neither category displays an overwhelmingly strong pattern</strong></li>
                <li><strong>All categories have denser spread in bottom half of graph. However, considerable amount of points can be observed in top half as well</strong></li>
                <li><strong>While neuro-divergence categories haven't shown strong tendencies, overall we can interpret that presence of gaming as a hobby seems related to wellbeing index</strong></li>
            </ul>
        </div>
        """,
        width=650, height=410
        )


        return layout(
                    [
                        [title],  # Row 1: Title
                        [column(wellbeing_playtime_scatter())],  # Row 2: Two columns
                        [observations]
                    ]
                )

    def create_slide_7(self):
        """Conclusion"""

        title = Div(
            text="""
            <div style="
                background: #0D2152;
                border: 3px solid #C5CFDC;
                border-radius: 20px;
                padding: 30px 5px 20px 32px;
                margin: 18px 0;
                width: 950px;
                max-width: 950px;
                font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
            ">
                <h3 style="
                    color: #FFF9E6;
                    font-size: 1.8em; font-weight: bold;
                    margin-top: 0; margin-bottom: 10px;
                    letter-spacing: 1px;
                    text-shadow: 0 2px 20px #f59e0b55;
                    @font-face {
                        font-family: "Press Start 2P";
                        src: url("PressStart2P-Regular.ttf") format("ttf"),
                        };
                ">
                    Final Thoughts
                </h3>
            """
        )

        observations = Div(
        text="""
        <div style="
            background: #0D2152;
            border: 3px solid #C5CFDC;
            border-radius: 20px;
            padding: 30px 32px 20px 32px;
            margin: 18px 0;
            width: 950px;
            max-width: 950px;
            font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
        ">

            <h4 style="color: #F4F2ED; font-size: 1.5em; margin-bottom: 10px; margin-top: 0;">A strong relationship between playtime and wellbeing index can be observed</h4>
            <ul style="color: #F4F2ED; font-size: 1.3em; padding-left: 17px; margin-top: 0;">
                <li><strong>The dataset presents a vast future scope to explore relationships and patterns between further demographics</strong></li>
                <li><strong>The long duration of telemetry as well as availability of the surverys could also allow possibilities of DID studies with respect to stressful situations at home or larger culural phenomenons</strong></li>
            </ul>
        </div>
        """,
        width=650, height=410
        )


        # === LAYOUT COMPOSITION ===
        return layout(
            [
                [title],  # Row 1: Title
                [observations],  # Row 2: Two columns
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
        )

        # === MAIN CONTENT AREA ===
        self.main_content = column(self.slides[0])

        # === FULL APPLICATION LAYOUT ===
        self.layout = column(
            nav_bar,  # Navigation controls
            Div(text="<hr>", width=1, height=5),  # Visual separator
            self.slide_select,
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

        self.prev_button.disabled = self.current_slide == 0
        self.next_button.disabled = self.current_slide == self.total_slides - 1
        self.main_content.children = [self.slides[self.current_slide]]
        self.slide_select.value = str(self.current_slide)

        # Server-side logging (appears in terminal, not browser)
        print(
            f"Showing slide {self.current_slide + 1}: {self.get_slide_title(self.current_slide)}"
        )

presentation = InteractivePresentation()

curdoc().add_root(presentation.layout)
curdoc().title = "Open Play Analysis"
output_file(filename="Open_Play_Analysis.html", title="Open_Play_Analysis")

# Server Side logging
print("=" * 50)
print("Interactive Presentation App Started!")
print("=" * 50)
print("Navigate through slides using controls")
print("All visualizations are interactive")
print("Try Auto Play for presentation mode")
print("=" * 50)

