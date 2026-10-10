
from bokeh.plotting import figure, curdoc
from bokeh.models import (
    Div,  # HTML div element for custom HTML/CSS content
    Button,  # Interactive button widget - triggers Python callbacks on click
    Select,  # Dropdown selection widget - triggers callbacks on selection
    InlineStyleSheet
)

from bokeh.layouts import (
    column,  # Vertical layout - stacks elements top to bottom
    row,  # Horizontal layout - places elements side by side
    layout,  # Grid layout - accepts nested lists for complex layouts
    # Example: layout([[plot1, plot2], [plot3]]) creates 2 rows
)

from bokeh.themes.theme import Theme

import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from hourly_unit import hourly_unit
from wellbeing_vs_playtime_graph import create_playtime_spikes_wellbeing_graph
from keywords_vs_gender import keywords_vs_gender
from low_wellbeing_control import create_low_wellbeing_control_grid

class InteractivePresentation:
    """
    Main application class for the Bokeh presentation system.
    """

    def __init__(self):
        self.current_slide = 0  # Track which slide is currently displayed
        self.total_slides = 6  # Total number of slides in presentation
        self.slides = []  # Will hold Bokeh layout objects for each slide
        self.auto_play = False  # Flag for auto-advance mode
        self.auto_play_callback = (None)
        self.create_slides()
        self.create_navigation()
        self.create_layout()
        self.colors = {
            "yellow": "#f8f4c7",
            "black" : "#343838",
            "pink"  : "#ee3377", 
            "navy"  : "#0072b2",
            "teal"  : "#33bbee",
            "green" : "#009e73"

        }

    def create_navigation(self):
        """
        Create navigation controls
        """

        styles = InlineStyleSheet(
            css=""" .bk-btn {
            align-items: center;
            background-color: #f8f4c7;
            border: 2px solid #111;
            border-radius: 8px;
            box-sizing: border-box;
            color: #111;
            cursor: pointer;
            display: flex;
            font-family: Inter,sans-serif;
            font-size: 16px;
            height: 48px;
            justify-content: center;
            line-height: 24px;
            max-width: 100%;
            padding: 0 25px;
            position: relative;
            text-align: center;
            text-decoration: none;
            user-select: none;
            -webkit-user-select: none;
            touch-action: manipulation;
            }

            .bk-btn:after {
            background-color: #111;
            border-radius: 8px;
            content: "";
            display: block;
            height: 48px;
            left: 0;
            width: 100%;
            position: absolute;
            top: -2px;
            transform: translate(8px, 8px);
            transition: transform .2s ease-out;
            z-index: -1;
            }

            .bk-btn:hover:after {
            transform: translate(0, 0);
            }

            .bk-btn:active {
            background-color: #f8f4c7;
            outline: 0;
            }

            .bk-btn:hover {
            outline: 0;
            }

            @media (min-width: 100px) {
            .bk-btn {
                padding: 0 40px;
            }
            }"""
        )

        self.prev_button = Button(
            label="◀ Previous", stylesheets=[styles]
        )
        self.next_button = Button(
            label="Next ▶", stylesheets=[styles]
        )
        self.home_button = Button(
            label="🏠 Home", stylesheets=[styles]
        )

        self.prev_button.on_click(self.prev_slide)
        self.next_button.on_click(self.next_slide)
        self.home_button.on_click(self.go_home)

    def get_slide_title(self, index):
        """Get title for each slide"""
        titles = [
            "The Dataset",
            "Who plays when?",
            "When play time spikes (why?), does it affect the wellbeing?",
            "Does gaming make us unhappy?",
            "Patterns in Gender-wise Game Preference",
            "Conclusion"
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
            self.create_slide_6()
        ]

    def create_slide_1(self):
        """Welcome and Introduction"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            🎮 Open Play Dataset (v1.2.6)
        </h1>
        """,
            width=800,  # Fixed width in pixels
            height=80,  # Fixed height in pixels
        )

        dashboard = Div(
        text="""
        <div style="
            background: #f8f4c7;
            border: 2.5px solid #343838;
            border-radius: 20px;
            padding: 30px 32px 20px 32px;
            margin: 18px 0;
            min-width: 520px;
            max-width: 720px;
            box-shadow: 0 8px 32px #8b5cf655, 0 2px 24px #000c;
            font-family: 'Fira Code', 'Menlo', 'Consolas', monospace;
        ">
            <h2 style="
                color: #f59e0b; 
                font-size: 2em; font-weight: bold; 
                margin-top: 0; margin-bottom: 10px; 
                letter-spacing: 1px; 
                text-shadow: 0 2px 20px #f59e0b55;
                @font-face {
                    font-family: "Press Start 2P";
                    src: url("PressStart2P-Regular.ttf") format("ttf"),
                }
            ">
                🎮 Open Play Dataset (v1.2.6)
            </h2>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 20px;">
                <div>
                    <h4 style="color: #06b6d4; font-size: 1.14em; margin-bottom: 10px;">📋 Project Details</h4>
                    <ul style="color: #f9fafb; font-size: 1.07em; padding-left: 17px; margin-top: 0;">
                        <li><strong>Languages:</strong> Python, JS, Rust</li>
                        <li><strong>Framework:</strong> React</li>
                        <li><strong>Name:</strong> NebulaOps</li>
                        <li><strong>Description:</strong> A modern dashboard demo for Bokeh.</li>
                    </ul>
                </div>
                <div>
                    <h4 style="color: #f59e0b; font-size: 1.14em; margin-bottom: 10px;">⚙️ Configuration</h4>
                    <ul style="color: #f9fafb; font-size: 1.07em; padding-left: 17px; margin-top: 0;">
                        <li><strong>Environment:</strong> 🚀 Production</li>
                        <li><strong>Features:</strong> 🐛 Debug, 📊 Analytics</li>
                        <li><strong>Performance:</strong> 8/10</li>
                        <li><strong>Budget:</strong> $25K - $70K</li>
                    </ul>
                </div>
            </div>
            
        """,
        width=650, height=410
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
                    column(dashboard)
                ],  # Row 2: Two columns
            ]
        )

    def create_slide_2(self):
        """Demographic Exploration"""

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
                            hourly_unit()
                        ],  # Row 2: Two columns
                    ]
                )

    def create_slide_3(self):
        """Playtime Spikes & Wellbeing Index"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            When playtimes spike (why?), does the wellbeing index increase too?
        </h1>

        """,
            width=800,
        )

        return layout(
                    [
                        [title],  # Row 1: Title
                        [
                            column(create_playtime_spikes_wellbeing_graph())
                        ],  # Row 2: Two columns
                    ]
                )
        
    def create_slide_4(self):
        """How does gaming affect our sense of control?"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            The relationship between wellbeing index and loss of control of gaming time
        </h1>

        """,
            width=800,
        )

        return layout(
                    [
                        [title],  # Row 1: Title
                        [
                            column(create_low_wellbeing_control_grid())
                        ],  
                    ]
                )

    def create_slide_5(self):
        """Gender-wise Preferences"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            Do people of a gender, game together?
        </h1>

        """,
            width=1200
        )

        return layout(
                    [
                        [title],  # Row 1: Title
                        [
                            column(keywords_vs_gender())
                        ],  # Row 2: Two columns
                    ]
                )

    def create_slide_6(self):
        """Conclusion"""

        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            Final Takeaways
        </h1>
        """,
            width=1000,  # Fixed width in pixels
            height=100,  # Fixed height in pixels
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

        self.prev_button.disabled = self.current_slide == 0
        self.next_button.disabled = self.current_slide == self.total_slides - 1
        self.main_content.children = [self.slides[self.current_slide]]

        # Server-side logging (appears in terminal, not browser)
        print(
            f"Showing slide {self.current_slide + 1}: {self.get_slide_title(self.current_slide)}"
        )

presentation = InteractivePresentation()

curdoc().add_root(presentation.layout)
curdoc().title = "Open Play Analysis"
curdoc().theme = Theme("theme.yaml")

# Server Side logging
print("=" * 50)
print("Interactive Presentation App Started!")
print("=" * 50)
print("Navigate through slides using controls")
print("All visualizations are interactive")
print("Try Auto Play for presentation mode")
print("=" * 50)

