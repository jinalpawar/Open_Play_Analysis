"""Export the Bokeh presentation (open_play_analysis/main.py) to ONE standalone HTML file.

Why this script: in main.py the Previous / Next / Home buttons and the "Jump to" menu use Python
callbacks (on_click, on_change). Those only work with `bokeh serve`. In a plain HTML file there is
no Python, so here we rebuild the same presentation and replace those callbacks with small
JavaScript callbacks (CustomJS). The CSS is also put inside the file, so the HTML works alone.

Run from the repository root (where the CSV files are):
    uv run python export_html.py
Output: Open_Play_Analysis.html
"""
import sys
from pathlib import Path

from bokeh.io import save
from bokeh.models import CustomJS, InlineStyleSheet, GlobalInlineStyleSheet
from bokeh.resources import INLINE

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "open_play_analysis"))   # so that "from slides..." works as in main.py

import main  # builds the presentation exactly as in the app (main.presentation)

p = main.presentation
static = ROOT / "open_play_analysis" / "static"

# 1) CSS inside the file instead of links to open_play_analysis/static/*.css
style = InlineStyleSheet(css=(static / "styles.css").read_text())
global_style = GlobalInlineStyleSheet(css=(static / "global.css").read_text())
p.prev_button.stylesheets = [style, global_style]
p.next_button.stylesheets = [style]
p.home_button.stylesheets = [style]

# 2) All slides are in the page; only the current one is visible
for i, slide in enumerate(p.slides):
    slide.visible = (i == 0)
p.main_content.children = list(p.slides)
p.slide_select.value = "0"
p.prev_button.disabled = True
p.next_button.disabled = False

# 3) Navigation in JavaScript. The "Jump to" menu holds the current slide number;
#    the buttons only change its value, and this callback shows the right slide.
p.slide_select.js_on_change("value", CustomJS(
    args=dict(slides=p.slides, prev=p.prev_button, next=p.next_button, n=len(p.slides)),
    code="""
    const i = parseInt(cb_obj.value);
    slides.forEach((s, k) => { s.visible = (k === i); });
    prev.disabled = (i === 0);
    next.disabled = (i === n - 1);
    window.scrollTo(0, 0);
"""))
p.prev_button.js_on_click(CustomJS(args=dict(sel=p.slide_select),
    code="sel.value = String(Math.max(0, parseInt(sel.value) - 1));"))
p.next_button.js_on_click(CustomJS(args=dict(sel=p.slide_select, n=len(p.slides)),
    code="sel.value = String(Math.min(n - 1, parseInt(sel.value) + 1));"))
p.home_button.js_on_click(CustomJS(args=dict(sel=p.slide_select), code="sel.value = '0';"))

# 4) Python callbacks cannot run in a static file: remove them to avoid warnings
for widget in (p.prev_button, p.next_button, p.home_button):
    widget._event_callbacks = {}
p.slide_select._callbacks = {}

out = ROOT / "Open_Play_Analysis.html"
save(p.layout, filename=str(out), resources=INLINE, title="Open Play Analysis")
print("Saved", out)
