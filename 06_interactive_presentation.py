#!/usr/bin/env python
"""
Interactive Presentation App with Bokeh
Run with: bokeh serve 06_interactive_presentation.py
Then open: http://localhost:5006/06_interactive_presentation

=== BOKEH SERVER ARCHITECTURE ===
Bokeh Server creates a bidirectional websocket connection between Python and the browser.
This allows:
1. Python callbacks to run on the server (not in JavaScript)
2. Real-time updates from server to client
3. Stateful applications with server-side logic
4. Multiple clients connecting to the same app instance
"""

# === CORE BOKEH IMPORTS ===
# figure: The main plotting interface - creates a Plot object with axes, grids, tools
# curdoc: Current document - represents the Bokeh document that will be synchronized to the browser
from bokeh.plotting import figure, curdoc

# === BOKEH MODELS ===
# Models are the building blocks of Bokeh applications
# Each model represents a component that can be rendered in the browser
from bokeh.models import (
    # === WIDGETS ===
    Div,  # HTML div element for custom HTML/CSS content
    Button,  # Interactive button widget - triggers Python callbacks on click
    Slider,  # Numeric slider widget - triggers callbacks on value change
    Select,  # Dropdown selection widget - triggers callbacks on selection
    # === DATA HANDLING ===
    ColumnDataSource,  # CRITICAL: Bokeh's fundamental data structure
    # - Holds columnar data (like a DataFrame)
    # - Automatically syncs between Python and JavaScript
    # - Updates to .data property trigger re-rendering
    # - Enables streaming, patching, and efficient updates
    # === TOOLS ===
    HoverTool,  # Interactive hover tooltips - shows data on mouse hover
    # - Can use @ prefix to reference column names
    # - Supports custom HTML formatting
    # === COLOR MAPPING ===
    LinearColorMapper,  # Maps numeric values to colors linearly
    # - Used for heatmaps, choropleth maps
    # - Requires palette (list of colors) and low/high range
    ColorBar,  # Visual legend for color mappers
    # - Shows the color scale with numeric labels
    # === FORMATTING ===
    BasicTicker,  # Controls tick mark locations on axes
    PrintfTickFormatter,  # Formats tick labels using printf-style strings
)

# === LAYOUT SYSTEM ===
# Bokeh uses a responsive layout system similar to CSS flexbox
from bokeh.layouts import (
    column,  # Vertical layout - stacks elements top to bottom
    row,  # Horizontal layout - places elements side by side
    layout,  # Grid layout - accepts nested lists for complex layouts
    # Example: layout([[plot1, plot2], [plot3]]) creates 2 rows
)

# === COLOR PALETTES ===
# Bokeh provides pre-defined color palettes for consistent styling
from bokeh.palettes import (
    RdYlBu11,  # Red-Yellow-Blue diverging palette with 11 colors
    # Good for showing positive/negative values
    Category20,  # Categorical palette with up to 20 distinct colors
    # Dictionary with keys for different numbers of colors (3,4,5...20)
)

# === TRANSFORMS ===
# Transforms are client-side operations that happen in the browser
from bokeh.transform import (
    factor_cmap,  # Maps categorical factors to colors
    # More efficient than manually assigning colors
)

# Standard Python libraries
import numpy as np
import pandas as pd
import base64  # For encoding images as base64 strings to embed in HTML
import os


class InteractivePresentation:
    """
    Main application class for the Bokeh presentation system.

    === BOKEH APPLICATION PATTERN ===
    This follows the Object-Oriented pattern for Bokeh apps:
    1. Initialize state variables
    2. Create UI components (widgets, plots)
    3. Set up callbacks (event handlers)
    4. Compose layout
    5. Add to document

    The class encapsulates all presentation logic and state.
    """

    def __init__(self):
        # === STATE MANAGEMENT ===
        # Bokeh server apps are stateful - these variables persist across callbacks
        self.current_slide = 0  # Track which slide is currently displayed
        self.total_slides = 7  # Total number of slides in presentation
        self.slides = []  # Will hold Bokeh layout objects for each slide
        self.auto_play = False  # Flag for auto-advance mode
        self.auto_play_callback = (
            None  # Reference to periodic callback for cleanup
        )

        # === INITIALIZATION ORDER MATTERS ===
        # 1. Create slides first (generates all content)
        self.create_slides()

        # 2. Create navigation (needs to know about slides)
        self.create_navigation()

        # 3. Create main layout (combines slides + navigation)
        self.create_layout()

    def create_navigation(self):
        """Create navigation controls

        === BOKEH WIDGETS ===
        Widgets are interactive components that trigger Python callbacks.
        Unlike JavaScript frameworks, these callbacks run on the SERVER.
        """

        # === BUTTON WIDGETS ===
        # Button constructor parameters:
        # - label: Text displayed on button (supports Unicode emoji)
        # - button_type: Bootstrap-style types ("default", "primary", "success", "warning", "danger")
        # - width/height: Size in pixels (responsive by default if not set)
        # - disabled: Boolean to enable/disable interaction
        self.prev_button = Button(
            label="◀ Previous", button_type="primary", width=100
        )
        self.next_button = Button(
            label="Next ▶", button_type="primary", width=100
        )
        self.home_button = Button(
            label="🏠 Home", button_type="warning", width=100
        )

        # # Auto-play controls
        # self.play_button = Button(
        #     label="▶ Auto Play", button_type="success", width=100
        # )
        # self.stop_button = Button(
        #     label="⏸ Stop", button_type="danger", width=100
        # )

        # === SELECT WIDGET ===
        # Select creates a dropdown menu
        # Options format: List of tuples (value, label)
        # - value: What gets stored in widget.value (usually string)
        # - label: What user sees in dropdown
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

        # === DIV WIDGET ===
        # Div renders arbitrary HTML/CSS
        # SECURITY NOTE: Bokeh sanitizes HTML to prevent XSS attacks
        # Supports inline styles and basic HTML tags
        self.progress_div = Div(
            text=self.get_progress_html(),  # HTML string
            width=200,  # Width in pixels
        )

        # === CALLBACK ATTACHMENT ===
        # CRITICAL CONCEPT: Callbacks in Bokeh Server
        # These callbacks run in PYTHON on the SERVER, not JavaScript in browser
        # When user clicks button → browser sends message → server runs Python function → updates sent back

        # Button callbacks: .on_click(function)
        # Function receives no arguments (for buttons)
        self.prev_button.on_click(self.prev_slide)
        self.next_button.on_click(self.next_slide)
        self.home_button.on_click(self.go_home)
        # self.play_button.on_click(self.start_auto_play)
        # self.stop_button.on_click(self.stop_auto_play)

        # Property change callbacks: .on_change("property_name", function)
        # Function receives (attr, old_value, new_value)
        # Common properties: "value", "active", "data"
        self.slide_select.on_change("value", self.jump_to_slide)

    def get_slide_title(self, index):
        """Get title for each slide"""
        titles = [
            "Welcome",
            "Visual Vocabulary",
            "Data Overview",
            "Interactive Analysis",
            "Time Series Trends",
            "Correlation Explorer",
            "Conclusions",
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
            self.create_slide_1_welcome(),
            self.create_slide_2_visual_vocabulary(),
            self.create_slide_3_overview(),
            self.create_slide_4_interactive(),
            self.create_slide_5_timeseries(),
            self.create_slide_6_correlation(),
            self.create_slide_7_conclusions(),
        ]

    def create_slide_1_welcome(self):
        """Slide 1: Welcome and Introduction

        === SLIDE CREATION PATTERN ===
        Each slide method returns a Bokeh layout object.
        Slides can contain:
        - Static content (Div with HTML)
        - Interactive plots (figure objects)
        - Widgets (buttons, sliders, etc.)
        - Nested layouts (rows, columns)
        """

        # === HTML CONTENT IN DIV ===
        # Div widget renders HTML content
        # Triple quotes allow multi-line strings
        # Bokeh sanitizes HTML but allows:
        # - Basic tags: h1-h6, p, div, span, ul, ol, li, table, etc.
        # - Inline styles via style attribute
        # - CSS classes (but need external CSS for definitions)
        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            📊 Interactive Data Presentation with Bokeh
        </h1>
        """,
            width=800,  # Fixed width in pixels
            height=80,  # Fixed height in pixels
        )

        # === PREPARING DATA FOR BOKEH ===
        # Generate random data for demonstration
        n_points = 100
        x = np.random.randn(n_points)  # Random normal distribution
        y = np.random.randn(n_points)
        colors = np.random.choice(
            ["red", "green", "blue", "yellow", "purple"], n_points
        )
        sizes = np.random.randint(10, 30, n_points)  # Random sizes 10-30 pixels

        # === COLUMNDATASOURCE - BOKEH'S DATA MODEL ===
        # ColumnDataSource is FUNDAMENTAL to Bokeh:
        # 1. Holds data in columnar format (like a DataFrame)
        # 2. Synchronizes between Python and JavaScript automatically
        # 3. Enables efficient updates (only changed data is sent)
        # 4. All glyphs reference columns by name using strings
        #
        # Data format: dict with column names as keys, arrays/lists as values
        # All columns must have same length!
        source = ColumnDataSource(
            data=dict(
                x=x,  # Column "x" with x-coordinates
                y=y,  # Column "y" with y-coordinates
                colors=colors,  # Column "colors" with color values
                sizes=sizes,  # Column "sizes" with size values
            )
        )

        # === CREATING FIGURES ===
        # figure() creates a Plot with default axes, grids, and tools
        # Common parameters:
        # - width/height: Size in pixels
        # - title: Plot title
        # - x_range/y_range: Data ranges (auto-calculated if not specified)
        # - tools: String of tool names or list of Tool objects
        # - toolbar_location: "above", "below", "left", "right", None
        p = figure(
            width=600, height=400, title="Welcome to Interactive Visualization"
        )

        # === ADDING GLYPHS ===
        # Glyphs are the visual elements (circles, lines, bars, etc.)
        # scatter() is a convenience method that creates circle glyphs
        #
        # CRITICAL: Column references use STRINGS not actual data!
        # - "x", "y" refer to column names in the source
        # - "sizes", "colors" also reference column names
        #
        # When source updates, plot automatically re-renders
        p.scatter(
            "x",
            "y",  # Position columns (required)
            size="sizes",  # Size column (can be scalar or column name)
            color="colors",  # Color column (can be scalar or column name)
            alpha=0.6,  # Transparency (0=transparent, 1=opaque)
            source=source,  # Data source (ColumnDataSource)
        )

        # Info panels
        features = Div(
            text="""
        <div style="background-color: #ecf0f1; padding: 20px; border-radius: 10px;">
            <h3>Researchers from University of Oxford, Tilburg University, Karolinska Institute presented telemetry data collected from Nintendo, Steam and Microsoft for ~2,000 individuals across 43 months. During this period, they also carried out a 12-week survey for these participants to understand their gaming preferences and mental wellbeing.</h3>
            <ul style="font-size: 14px;">
                <li>📱 <b>Fully Interactive:</b> All plots support zoom, pan, and hover</li>
                <li>🔄 <b>Real-time Updates:</b> Dynamic data visualization</li>
                <li>🎮 <b>User Controls:</b> Sliders, buttons, and selections</li>
                <li>📊 <b>Multiple Chart Types:</b> Line, scatter, bar, heatmap</li>
                <li>🔗 <b>Linked Visualizations:</b> Selections across multiple plots</li>
                <li>⏯️ <b>Auto-play Mode:</b> Automatic slide progression</li>
            </ul>
        </div>
        """,
            width=1000,
            height=300,
        )

        instructions = Div(
            text="""
        <div style="background-color: #e8f4f8; padding: 20px; border-radius: 10px;">
            <h3>🎮 Navigation:</h3>
            <ul style="font-size: 14px;">
                <li>Use <b>Next/Previous</b> buttons to navigate</li>
                <li>Select specific slides from dropdown</li>
                <li>Click <b>Auto Play</b> for presentation mode</li>
                <li>All visualizations are interactive!</li>
            </ul>
        </div>
        """,
            width=400,
            height=200,
        )

        # Animate button
        animate_btn = Button(label="🎨 Shuffle Data", button_type="success")

        # === UPDATING DATA IN BOKEH ===
        # This callback demonstrates the key pattern for updating plots
        def animate():
            # Generate new random data
            new_x = np.random.randn(n_points)
            new_y = np.random.randn(n_points)
            new_colors = np.random.choice(
                ["red", "green", "blue", "yellow", "purple"], n_points
            )
            new_sizes = np.random.randint(10, 30, n_points)

            # === CRITICAL: How to update ColumnDataSource ===
            # Option 1: Replace entire .data dictionary (used here)
            # This triggers a full update of the plot
            source.data = dict(
                x=new_x, y=new_y, colors=new_colors, sizes=new_sizes
            )

            # Option 2: Update individual columns (not shown)
            # source.data["x"] = new_x  # DON'T do this - won't trigger update
            #
            # Option 3: Use .patch() for partial updates (not shown)
            # source.patch({"x": [(slice(5, 10), new_x[5:10])]})
            #
            # Option 4: Use .stream() to append data (not shown)
            # source.stream({"x": [1, 2], "y": [3, 4], ...})

        # Attach callback - will run on server when button clicked
        animate_btn.on_click(animate)

        # === LAYOUT COMPOSITION ===
        # layout() accepts nested lists to create grid layouts
        # Each list is a row, items in list are columns
        #
        # Structure here:
        # Row 1: [title] - single item spans full width
        # Row 2: [column(plot, button), column(features, instructions)]
        #        Creates 2 columns side by side
        #
        # column() stacks items vertically
        # row() places items horizontally
        # layout() creates responsive grid from nested lists
        return layout(
            [
                [title],  # Row 1: Title
                [
                    column(p),
                    column(features, instructions)
                ],  # Row 2: Two columns
            ]
        )

    def create_slide_2_visual_vocabulary(self):
        """Slide 2: Visual Vocabulary - FT Guide"""
        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            📊 Visual Vocabulary - Financial Times Guide
        </h1>
        <p style="text-align: center; font-size: 16px;">
            A comprehensive guide to selecting the right chart type for your data story
        </p>
        """,
            width=1200,
            height=100,
        )

        # === EMBEDDING IMAGES IN BOKEH ===
        # Since Bokeh apps run on a server, image paths can be tricky
        # Solution: Encode image as base64 and embed directly in HTML
        #
        # This ensures image displays regardless of server configuration
        image_path = os.path.join(
            os.path.dirname(__file__), "visual-vocabulary-ft.png"
        )
        image_html = ""

        if os.path.exists(image_path):
            # Read image file as binary
            with open(image_path, "rb") as img_file:
                # Encode to base64 string
                encoded_string = base64.b64encode(img_file.read()).decode()

                # === DATA URI SCHEME ===
                # Format: data:[<mediatype>][;base64],<data>
                # This embeds the entire image in the HTML
                # Pros: No external file dependencies
                # Cons: Larger HTML size
                image_html = f"""
        <div style="text-align: center; margin: 20px auto;">
            <img src="data:image/png;base64,{encoded_string}" 
                 style="max-width: 100%; height: auto; max-height: 600px; border: 2px solid #ddd; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"
                 alt="Visual Vocabulary - Financial Times">
        </div>
        """
        else:
            # Fallback if image not found
            image_html = """
        <div style="text-align: center; margin: 20px auto; padding: 50px; background-color: #f0f0f0; border-radius: 10px;">
            <h3>Visual Vocabulary Image</h3>
            <p>Image file not found: visual-vocabulary-ft.png</p>
            <p>Please ensure the image is in the same directory as this script.</p>
        </div>
        """

        # Main image display
        image_div = Div(
            text=image_html,
            width=1200,
            height=650,
        )

        # Information panel
        info_panel = Div(
            text="""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3>📌 About the Visual Vocabulary</h3>
            <p>The Financial Times Visual Vocabulary is a poster and guide that helps you select the most appropriate chart type based on the story you want to tell with your data.</p>
            <div style="display: flex; justify-content: space-around; margin-top: 15px;">
                <div style="flex: 1; margin: 0 10px;">
                    <h4>Categories Include:</h4>
                    <ul style="font-size: 14px;">
                        <li><b>Deviation</b> - Emphasize variations</li>
                        <li><b>Correlation</b> - Show relationships</li>
                        <li><b>Ranking</b> - Show order</li>
                        <li><b>Distribution</b> - Show frequency</li>
                        <li><b>Change over Time</b> - Show trends</li>
                    </ul>
                </div>
                <div style="flex: 1; margin: 0 10px;">
                    <h4>More Categories:</h4>
                    <ul style="font-size: 14px;">
                        <li><b>Magnitude</b> - Show size comparisons</li>
                        <li><b>Part-to-whole</b> - Show components</li>
                        <li><b>Spatial</b> - Show geographical data</li>
                        <li><b>Flow</b> - Show transfers</li>
                    </ul>
                </div>
            </div>
            <p style="margin-top: 15px; font-style: italic;">💡 <b>Tip:</b> Use this guide when deciding how to visualize your data. Consider what story you want to tell and find the appropriate category and chart type.</p>
        </div>
        """,
            width=1200,
            height=250,
        )

        return layout([[title], [image_div], [info_panel]])

    def create_slide_3_overview(self):
        """Slide 3: Data Overview with Multiple Charts"""
        title = Div(
            text="""
        <h2 style="color: #2c3e50;">📈 Data Overview Dashboard</h2>
        <p>Multiple synchronized visualizations showing different aspects of the dataset</p>
        """,
            width=800,
        )

        # Generate sample data
        categories = [
            "Product A",
            "Product B",
            "Product C",
            "Product D",
            "Product E",
        ]
        years = ["2020", "2021", "2022", "2023", "2024"]

        # === USING PANDAS WITH BOKEH ===
        # ColumnDataSource can be created directly from DataFrames
        # Column names become the keys in the data dictionary
        bar_data = pd.DataFrame(
            {
                "categories": categories,
                "values": np.random.randint(50, 200, len(categories)),
            }
        )
        # Creating ColumnDataSource from DataFrame
        # Bokeh automatically converts DataFrame columns to dict format
        bar_source = ColumnDataSource(bar_data)

        # Line chart data
        line_data = pd.DataFrame(
            {"x": range(50), "y": np.cumsum(np.random.randn(50)) + 100}
        )
        line_source = ColumnDataSource(line_data)

        # Pie chart simulation (using wedge)
        angles = [0, 72, 144, 216, 288]
        colors = Category20[5]
        percentages = np.random.randint(10, 30, 5)
        percentages = percentages / percentages.sum() * 100

        # Create plots
        # 1. Bar chart
        # === CATEGORICAL AXES ===
        # When x_range is a list of strings, Bokeh creates categorical axis
        # Each category gets equal space on the axis
        p1 = figure(
            x_range=categories,  # List of category names for x-axis
            width=400,
            height=300,
            title="Sales by Product",
            toolbar_location="above",  # Position of pan/zoom tools
        )

        # === VBAR GLYPH ===
        # vbar creates vertical bars (use hbar for horizontal)
        # Parameters:
        # - x: Category or numeric x-coordinate
        # - top: Height of bar (y-value at top)
        # - bottom: Base of bar (default 0)
        # - width: Bar width (0-1 for categories, pixels for numeric)
        p1.vbar(
            x="categories",  # Column name for x-positions
            top="values",  # Column name for bar heights
            width=0.8,  # 80% of category width
            source=bar_source,
            # === FACTOR_CMAP TRANSFORM ===
            # Maps categorical values to colors
            # Runs in browser (client-side) for efficiency
            color=factor_cmap(
                "categories",  # Column to map
                palette=Category20[5],  # List of colors
                factors=categories,  # List of unique values
            ),
        )
        # Ensure bars start at 0 (not auto-ranged)
        p1.y_range.start = 0

        # 2. Line chart
        p2 = figure(width=400, height=300, title="Trend Analysis")
        p2.line("x", "y", source=line_source, line_width=2, color="navy")
        p2.scatter("x", "y", source=line_source, size=5, color="navy", alpha=0.5)

        # 3. Heatmap
        # === PREPARING DATA FOR HEATMAPS ===
        # Heatmaps need:
        # 1. Two categorical dimensions (x and y)
        # 2. A value for each (x,y) combination
        # 3. Data in "long" format (one row per cell)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]

        # Generate data in long format
        # Each tuple is (x_category, y_category, value)
        heatmap_data = []
        for month in months:
            for day in days:
                heatmap_data.append((month, day, np.random.randint(0, 100)))

        hm_source = ColumnDataSource(
            data=dict(
                months=[x[0] for x in heatmap_data],
                days=[x[1] for x in heatmap_data],
                values=[x[2] for x in heatmap_data],
            )
        )

        p3 = figure(
            x_range=months,
            y_range=days,
            width=400,
            height=300,
            title="Activity Heatmap",
            toolbar_location="above",
        )

        # === COLOR MAPPING FOR HEATMAPS ===
        # LinearColorMapper maps numeric values to colors
        # - palette: List of colors (here reversed RdYlBu11 for red=high)
        # - low/high: Range of values to map
        # Values outside range are clamped to endpoints
        mapper = LinearColorMapper(
            palette=RdYlBu11[
                ::-1
            ],  # [::-1] reverses list (red for high values)
            low=0,  # Minimum value
            high=100,  # Maximum value
        )

        # === RECT GLYPH FOR HEATMAP ===
        # rect creates rectangles (perfect for heatmap cells)
        p3.rect(
            x="months",  # X-coordinate (categorical)
            y="days",  # Y-coordinate (categorical)
            width=1,  # Width (1 = full category width)
            height=1,  # Height (1 = full category height)
            source=hm_source,
            # === TRANSFORM SYNTAX ===
            # Dictionary with "field" and "transform" keys
            # Tells Bokeh to apply mapper to values from "values" column
            fill_color={"field": "values", "transform": mapper},
        )

        # === ADDING COLOR BAR LEGEND ===
        # ColorBar shows the color scale with numeric labels
        color_bar = ColorBar(
            color_mapper=mapper,  # The mapper to visualize
            width=8,  # Width in pixels
            location=(0, 0),  # Position within plot (0,0 = auto)
        )
        # add_layout adds the color bar to the plot
        # Position can be "left", "right", "above", "below"
        p3.add_layout(color_bar, "right")

        # Statistics panel
        stats = Div(
            text=f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h3>📊 Key Metrics:</h3>
            <table style="width: 100%;">
                <tr><td><b>Total Products:</b></td><td>{len(categories)}</td></tr>
                <tr><td><b>Average Sales:</b></td><td>${bar_data["values"].mean():.2f}</td></tr>
                <tr><td><b>Max Sales:</b></td><td>${bar_data["values"].max()}</td></tr>
                <tr><td><b>Growth Rate:</b></td><td>+{np.random.uniform(5, 15):.1f}%</td></tr>
                <tr><td><b>Data Points:</b></td><td>{len(line_data)}</td></tr>
            </table>
        </div>
        """,
            width=400,
            height=200,
        )

        return layout([[title], [p1, p2], [p3, stats]])

    def create_slide_4_interactive(self):
        """Slide 4: Interactive Analysis with Controls

        === INTERACTIVE PATTERN ===
        This slide demonstrates the key pattern for interactive Bokeh apps:
        1. Create data source
        2. Create plot using data source
        3. Create control widgets
        4. Define update function that modifies data source
        5. Attach update function to widget callbacks
        """
        title = Div(
            text="""
        <h2 style="color: #2c3e50;">🎮 Interactive Data Explorer</h2>
        <p>Adjust parameters to explore different data visualizations</p>
        """,
            width=800,
        )

        # === INSTANCE VARIABLES FOR CROSS-METHOD ACCESS ===
        # Using self. makes this source accessible to callback functions
        # Start with empty data - will be populated by update function
        self.slide4_source = ColumnDataSource(data=dict(x=[], y=[]))

        # Create plot
        p = figure(width=600, height=400, title="Interactive Function Plotter")
        self.slide4_line = p.line(
            "x", "y", source=self.slide4_source, line_width=2, color="blue"
        )

        # === CONTROL WIDGETS ===
        # Each widget that affects the visualization

        # Select widget for dropdown choices
        self.func_select = Select(
            title="Function:",  # Label
            value="sin",  # Initial selection
            options=[
                "sin",
                "cos",
                "exp",
                "log",
                "polynomial",
            ],  # Available choices
        )

        # === SLIDER WIDGETS ===
        # Sliders for continuous numeric input
        # Parameters:
        # - start/end: Range of values
        # - value: Initial value
        # - step: Increment when dragging
        # - title: Label displayed above slider
        self.param_slider = Slider(
            start=0.1,  # Minimum value
            end=5,  # Maximum value
            value=1,  # Initial value
            step=0.1,  # Step size
            title="Parameter",  # Label
        )
        self.points_slider = Slider(
            start=50, end=500, value=100, step=50, title="Number of Points"
        )
        self.noise_slider = Slider(
            start=0, end=1, value=0, step=0.05, title="Noise Level"
        )

        # === UPDATE CALLBACK FUNCTION ===
        # This function is called whenever a widget value changes
        # It reads widget values, computes new data, and updates the plot
        def update_slide4():
            # === READING WIDGET VALUES ===
            # Access current value through .value property
            func = self.func_select.value  # String from Select
            param = self.param_slider.value  # Float from Slider
            n_points = int(self.points_slider.value)  # Convert to int
            noise = self.noise_slider.value  # Float from Slider

            # Generate x-coordinates
            x = np.linspace(0, 10, n_points)

            # Calculate y-values based on selected function
            if func == "sin":
                y = np.sin(param * x)
            elif func == "cos":
                y = np.cos(param * x)
            elif func == "exp":
                y = np.exp(-param * x / 5)
            elif func == "log":
                y = np.log(param * x + 1)
            else:  # polynomial
                y = param * x**2 - 2 * x + 1

            # Add noise if requested
            if noise > 0:
                y += np.random.normal(0, noise, len(y))

            # === UPDATING THE DATA SOURCE ===
            # Replace entire data dictionary to trigger re-render
            # Bokeh automatically updates the plot when source.data changes
            self.slide4_source.data = dict(x=x, y=y)

            # === UPDATING PLOT PROPERTIES ===
            # Can also update plot properties directly
            # Changes are automatically synchronized to browser
            p.title.text = f"{func.upper()} Function (param={param:.1f}, noise={noise:.1f})"

        # === ATTACHING CALLBACKS TO WIDGETS ===
        # .on_change(property, callback) monitors property changes
        #
        # Callback signature: func(attr, old, new)
        # - attr: Name of changed attribute (e.g., "value")
        # - old: Previous value
        # - new: New value
        #
        # Using lambda to ignore parameters since update_slide4 doesn't need them
        # Lambda wraps update_slide4() to match expected signature
        self.func_select.on_change("value", lambda a, o, n: update_slide4())
        self.param_slider.on_change("value", lambda a, o, n: update_slide4())
        self.points_slider.on_change("value", lambda a, o, n: update_slide4())
        self.noise_slider.on_change("value", lambda a, o, n: update_slide4())

        # Initial update
        update_slide4()

        # Info panel
        info = Div(
            text="""
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px;">
            <h3>🎯 Try These:</h3>
            <ul>
                <li>Change function type</li>
                <li>Adjust parameter to modify shape</li>
                <li>Add noise for realistic data</li>
                <li>Change number of points</li>
            </ul>
            <p><b>Tip:</b> Combine different settings to see interesting patterns!</p>
        </div>
        """,
            width=300,
            height=200,
        )

        controls = column(
            self.func_select,
            self.param_slider,
            self.points_slider,
            self.noise_slider,
            info,
        )

        return layout([[title], [p, controls]])

    def create_slide_5_timeseries(self):
        """Slide 5: Time Series Analysis"""
        title = Div(
            text="""
        <h2 style="color: #2c3e50;">📅 Time Series Analysis</h2>
        <p>Exploring temporal patterns and trends</p>
        """,
            width=800,
        )

        # Generate time series data
        dates = pd.date_range("2023-01-01", periods=365, freq="D")
        base_trend = np.linspace(100, 150, 365)
        seasonal = 10 * np.sin(np.arange(365) * 2 * np.pi / 365)
        noise = np.random.randn(365) * 5
        values = base_trend + seasonal + noise

        # Create moving averages
        ma7 = pd.Series(values).rolling(window=7).mean()
        ma30 = pd.Series(values).rolling(window=30).mean()

        source = ColumnDataSource(
            data=dict(dates=dates, values=values, ma7=ma7, ma30=ma30)
        )

        # Create plot
        p = figure(
            width=800,
            height=400,
            x_axis_type="datetime",
            title="Time Series with Moving Averages",
        )

        p.line(
            "dates",
            "values",
            source=source,
            line_width=1,
            color="lightgray",
            alpha=0.8,
            legend_label="Daily",
        )
        p.line(
            "dates",
            "ma7",
            source=source,
            line_width=2,
            color="blue",
            legend_label="7-day MA",
        )
        p.line(
            "dates",
            "ma30",
            source=source,
            line_width=2,
            color="red",
            legend_label="30-day MA",
        )

        p.legend.location = "top_left"
        p.legend.click_policy = "hide"

        # === HOVER TOOL CONFIGURATION ===
        # HoverTool shows tooltips when hovering over data
        hover = HoverTool(
            # === TOOLTIP SYNTAX ===
            # List of (label, value) tuples
            # @ prefix references column names in data source
            # {format} specifies formatting:
            # - {0.00} = 2 decimal places
            # - {%F} = datetime format (requires formatter)
            tooltips=[
                ("Date", "@dates{%F}"),  # Date with datetime formatting
                ("Value", "@values{0.00}"),  # Value with 2 decimals
                ("7-day MA", "@ma7{0.00}"),  # Moving average
                ("30-day MA", "@ma30{0.00}"),  # Moving average
            ],
            # === FORMATTERS ===
            # Special formatting for datetime/custom types
            # Key is column reference (@column), value is format type
            formatters={"@dates": "datetime"},
        )
        # Add tool to existing plot
        p.add_tools(hover)

        # Statistics
        stats = Div(
            text=f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h3>📈 Time Series Statistics:</h3>
            <table>
                <tr><td><b>Period:</b></td><td>{dates[0].strftime("%Y-%m-%d")} to {dates[-1].strftime("%Y-%m-%d")}</td></tr>
                <tr><td><b>Data Points:</b></td><td>{len(dates)}</td></tr>
                <tr><td><b>Mean:</b></td><td>{np.mean(values):.2f}</td></tr>
                <tr><td><b>Std Dev:</b></td><td>{np.std(values):.2f}</td></tr>
                <tr><td><b>Min:</b></td><td>{np.min(values):.2f}</td></tr>
                <tr><td><b>Max:</b></td><td>{np.max(values):.2f}</td></tr>
                <tr><td><b>Trend:</b></td><td>+{(values[-1] - values[0]):.2f}</td></tr>
            </table>
        </div>
        """,
            width=800,
            height=150,
        )

        return layout([[title], [p], [stats]])

    def create_slide_6_correlation(self):
        """Slide 6: Correlation Matrix Explorer"""
        title = Div(
            text="""
        <h2 style="color: #2c3e50;">🔗 Correlation Analysis</h2>
        <p>Exploring relationships between variables</p>
        """,
            width=800,
        )

        # Generate correlated data
        n_vars = 8
        n_samples = 100
        var_names = [f"Var_{i + 1}" for i in range(n_vars)]

        # Create correlation matrix
        data = np.random.randn(n_samples, n_vars)
        # Add some correlations
        data[:, 1] = data[:, 0] * 0.8 + np.random.randn(n_samples) * 0.2
        data[:, 2] = data[:, 0] * -0.6 + np.random.randn(n_samples) * 0.3
        data[:, 4] = data[:, 3] * 0.7 + np.random.randn(n_samples) * 0.3

        corr_matrix = np.corrcoef(data.T)

        # Prepare data for heatmap
        corr_data = []
        for i, var1 in enumerate(var_names):
            for j, var2 in enumerate(var_names):
                corr_data.append((var1, var2, corr_matrix[i, j]))

        source = ColumnDataSource(
            data=dict(
                var1=[x[0] for x in corr_data],
                var2=[x[1] for x in corr_data],
                corr=[x[2] for x in corr_data],
            )
        )

        # Create heatmap
        p = figure(
            x_range=var_names,
            y_range=list(reversed(var_names)),
            width=500,
            height=500,
            title="Correlation Matrix",
            toolbar_location="above",
            tools="hover,save",
        )

        mapper = LinearColorMapper(palette=RdYlBu11[::-1], low=-1, high=1)

        p.rect(
            "var1",
            "var2",
            width=1,
            height=1,
            source=source,
            fill_color={"field": "corr", "transform": mapper},
            line_color="white",
        )

        # === CONFIGURING HOVER AFTER CREATION ===
        # When tools="hover" is in figure(), can access via p.hover
        # Set tooltips property directly
        p.hover.tooltips = [
            ("Variables", "@var1 - @var2"),  # Combine two columns in display
            ("Correlation", "@corr{0.00}"),  # Format correlation to 2 decimals
        ]

        # Add color bar
        color_bar = ColorBar(
            color_mapper=mapper,
            width=8,
            location=(0, 0),
            ticker=BasicTicker(desired_num_ticks=10),
            formatter=PrintfTickFormatter(format="%.1f"),
        )
        p.add_layout(color_bar, "right")

        # Interpretation guide
        guide = Div(
            text="""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h3>📊 Interpretation Guide:</h3>
            <ul>
                <li><span style="color: darkblue;">■ Dark Blue:</span> Strong positive correlation (≈1.0)</li>
                <li><span style="color: lightblue;">■ Light Blue:</span> Weak positive correlation</li>
                <li><span style="color: yellow;">■ Yellow:</span> No correlation (≈0.0)</li>
                <li><span style="color: orange;">■ Orange:</span> Weak negative correlation</li>
                <li><span style="color: darkred;">■ Dark Red:</span> Strong negative correlation (≈-1.0)</li>
            </ul>
            <p><b>Hover</b> over cells to see exact correlation values</p>
        </div>
        """,
            width=300,
            height=300,
        )

        return layout([[title], [p, guide]])

    def create_slide_7_conclusions(self):
        """Slide 7: Conclusions and Summary"""
        title = Div(
            text="""
        <h1 style="text-align: center; color: #2c3e50;">
            🎯 Conclusions & Key Takeaways
        </h1>
        """,
            width=800,
            height=80,
        )

        # Summary cards
        card1 = Div(
            text="""
        <div style="background-color: #e8f4f8; padding: 20px; border-radius: 10px; margin: 10px;">
            <h3>✅ What We've Demonstrated</h3>
            <ul>
                <li>Interactive visualizations with real-time updates</li>
                <li>Multiple chart types and layouts</li>
                <li>User controls and parameter adjustments</li>
                <li>Linked data across multiple plots</li>
                <li>Time series analysis capabilities</li>
                <li>Statistical visualizations</li>
            </ul>
        </div>
        """,
            width=380,
            height=250,
        )

        card2 = Div(
            text="""
        <div style="background-color: #f0f8e8; padding: 20px; border-radius: 10px; margin: 10px;">
            <h3>🚀 Bokeh Server Advantages</h3>
            <ul>
                <li>Python callbacks for complex logic</li>
                <li>Real-time data streaming</li>
                <li>Server-side computation</li>
                <li>Multi-client support</li>
                <li>Stateful interactions</li>
                <li>Production-ready deployment</li>
            </ul>
        </div>
        """,
            width=380,
            height=250,
        )

        card3 = Div(
            text="""
        <div style="background-color: #fff0e8; padding: 20px; border-radius: 10px; margin: 10px;">
            <h3>📚 Use Cases</h3>
            <ul>
                <li>Business intelligence dashboards</li>
                <li>Scientific data exploration</li>
                <li>Real-time monitoring systems</li>
                <li>Interactive reports</li>
                <li>Educational tools</li>
                <li>Data storytelling</li>
            </ul>
        </div>
        """,
            width=380,
            height=250,
        )

        card4 = Div(
            text="""
        <div style="background-color: #f8e8f0; padding: 20px; border-radius: 10px; margin: 10px;">
            <h3>💡 Next Steps</h3>
            <ul>
                <li>Explore the source code</li>
                <li>Customize for your data</li>
                <li>Add more visualizations</li>
                <li>Deploy to production</li>
                <li>Integrate with databases</li>
                <li>Build your own apps!</li>
            </ul>
        </div>
        """,
            width=380,
            height=250,
        )

        # Thank you message
        thanks = Div(
            text="""
        <div style="text-align: center; margin-top: 30px;">
            <h2 style="color: #2c3e50;">Thank You! 🙏</h2>
            <p style="font-size: 16px;">
                This presentation was built entirely with Bokeh Server<br>
                All visualizations are live and interactive<br>
                <br>
                <b>Questions?</b> Explore the code and experiment!
            </p>
        </div>
        """,
            width=800,
            height=150,
        )

        return layout([[title], [card1, card2], [card3, card4], [thanks]])

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

    def start_auto_play(self):
        """Start auto-play mode

        === PERIODIC CALLBACKS IN BOKEH ===
        Bokeh can run functions periodically (like setInterval in JavaScript)
        """
        if not self.auto_play:
            self.auto_play = True

            # === ADD_PERIODIC_CALLBACK ===
            # Schedules function to run repeatedly
            # Returns callback ID for later removal
            # Parameters:
            # - callback function (no arguments)
            # - period in milliseconds
            self.auto_play_callback = curdoc().add_periodic_callback(
                self.auto_advance,  # Function to call
                5000,  # Period: 5000ms = 5 seconds
            )

            # Update button appearance to show state
            self.play_button.label = "⏸ Pause"
            self.play_button.button_type = "warning"
            print("Auto-play started")

    def stop_auto_play(self):
        """Stop auto-play mode"""
        if self.auto_play:
            self.auto_play = False

            # === REMOVE_PERIODIC_CALLBACK ===
            # Stop the periodic execution
            # Important: Must remove callbacks to prevent memory leaks
            if self.auto_play_callback:
                curdoc().remove_periodic_callback(self.auto_play_callback)

            # Reset button appearance
            self.play_button.label = "▶ Auto Play"
            self.play_button.button_type = "success"
            print("Auto-play stopped")

    def auto_advance(self):
        """Automatically advance to next slide"""
        self.next_slide()

    def create_layout(self):
        """Create the main layout

        === LAYOUT HIERARCHY ===
        Bokeh layouts are composable:
        - row() for horizontal arrangement
        - column() for vertical arrangement
        - layout() for grid (nested lists)
        - Spacer() for empty space (not used here)
        """

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
        # This will hold the current slide
        # Starting with first slide (index 0)
        self.main_content = column(self.slides[0])

        # === FULL APPLICATION LAYOUT ===
        # Vertical stack:
        # 1. Navigation bar
        # 2. Horizontal rule (separator)
        # 3. Main content (current slide)
        self.layout = column(
            nav_bar,  # Navigation controls
            Div(text="<hr>", width=1200, height=10),  # Visual separator
            self.main_content,  # Slide content
        )

        # Initialize display with first slide
        self.update_slide()


# === BOKEH SERVER APPLICATION ENTRY POINT ===
# This code runs when Bokeh server starts the application

# Create instance of our presentation class
presentation = InteractivePresentation()

# === ADDING TO DOCUMENT ===
# curdoc() returns the current Bokeh document
# This document is synchronized with the browser
# add_root() adds our layout as the root element
# Everything in the layout will be rendered in the browser
curdoc().add_root(presentation.layout)

# === DOCUMENT PROPERTIES ===
# Set browser tab title
curdoc().title = "Interactive Presentation"

# === SERVER-SIDE LOGGING ===
# These print statements appear in the terminal where bokeh serve is running
# Useful for debugging and monitoring server state
# Note: Users won't see these in their browser
print("=" * 50)
print("Interactive Presentation App Started!")
print("=" * 50)
print("Navigate through slides using controls")
print("All visualizations are interactive")
print("Try Auto Play for presentation mode")
print("=" * 50)

# === HOW BOKEH SERVER WORKS ===
# 1. User navigates to http://localhost:5006/06_interactive_presentation
# 2. Bokeh server creates new session for that user
# 3. This Python script runs, creating the document
# 4. Document is serialized and sent to browser
# 5. BokehJS renders the document in browser
# 6. User interactions trigger websocket messages to server
# 7. Server runs Python callbacks
# 8. Document updates are sent back to browser
# 9. BokehJS updates the display
#
# === IMPORTANT NOTES ===
# - Each user gets their own session (isolated state)
# - Python callbacks run on server (can access databases, files, etc.)
# - All data updates happen through ColumnDataSource
# - Layouts can be dynamically modified by changing .children
# - Widget states (.value, .disabled, etc.) auto-sync
# - Server maintains state between callbacks
# - Use print() for server-side debugging
# - Use Div with HTML for user-visible messages
