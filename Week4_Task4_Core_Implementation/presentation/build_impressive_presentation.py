"""
Build IMPRESSIVE PowerPoint Presentation for Saturday Review
Professional design with infographics, metrics, and visual appeal
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import nsmap
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
PLOTS_DIR = BASE_DIR / 'outputs' / 'eda_plots'
OUTPUT_DIR = Path(__file__).parent

# Professional Color Scheme
COLORS = {
    'primary': RGBColor(0, 82, 147),       # Deep blue
    'secondary': RGBColor(0, 150, 199),    # Cyan blue
    'accent': RGBColor(255, 152, 0),       # Orange
    'success': RGBColor(76, 175, 80),      # Green
    'danger': RGBColor(244, 67, 54),       # Red
    'warning': RGBColor(255, 193, 7),      # Yellow
    'dark': RGBColor(33, 37, 41),          # Dark gray
    'light': RGBColor(248, 249, 250),      # Light gray
    'white': RGBColor(255, 255, 255),
    'text': RGBColor(55, 65, 81),
}


def add_gradient_background(slide, prs, color1, color2):
    """Add a solid background (gradient requires complex XML)."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color1
    shape.line.fill.background()
    shape.shadow.inherit = False


def add_accent_bar(slide, prs, y_pos=Inches(0), height=Inches(0.15)):
    """Add a thin accent bar."""
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, y_pos, prs.slide_width, height
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = COLORS['accent']
    bar.line.fill.background()


def add_metric_box(slide, x, y, width, height, value, label, color):
    """Add a metric highlight box."""
    # Background box
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = color
    box.line.fill.background()

    # Value (large)
    val_box = slide.shapes.add_textbox(x, y + Inches(0.15), width, Inches(0.6))
    tf = val_box.text_frame
    p = tf.paragraphs[0]
    p.text = str(value)
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER

    # Label (small)
    lbl_box = slide.shapes.add_textbox(x, y + Inches(0.7), width, Inches(0.4))
    tf = lbl_box.text_frame
    p = tf.paragraphs[0]
    p.text = label
    p.font.size = Pt(12)
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER


def add_progress_indicator(slide, current, total, x, y):
    """Add slide progress dots."""
    for i in range(total):
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            x + i * Inches(0.25), y,
            Inches(0.1), Inches(0.1)
        )
        if i < current:
            dot.fill.solid()
            dot.fill.fore_color.rgb = COLORS['accent']
        else:
            dot.fill.solid()
            dot.fill.fore_color.rgb = RGBColor(200, 200, 200)
        dot.line.fill.background()


# ============================================================
# SLIDE TEMPLATES
# ============================================================

def create_title_slide(prs):
    """Slide 1: Impressive title slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    add_gradient_background(slide, prs, COLORS['primary'], COLORS['secondary'])

    # Decorative elements
    for i in range(3):
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(7 + i * 0.8), Inches(0.5 + i * 0.5),
            Inches(2), Inches(2)
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = RGBColor(255, 255, 255)
        fill = circle.fill
        fill.fore_color.rgb = RGBColor(255, 255, 255)
        # Set transparency via alpha
        circle.fill.solid()
        circle.fill.fore_color.rgb = RGBColor(255, 255, 255)
        circle.line.fill.background()

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(9), Inches(1.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Spatio-Temporal Prediction and"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "Risk Mapping of Groundwater"
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = COLORS['white']
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf.add_paragraph()
    p3.text = "Depletion in Karnataka"
    p3.font.size = Pt(36)
    p3.font.bold = True
    p3.font.color.rgb = COLORS['white']
    p3.alignment = PP_ALIGN.CENTER

    # Subtitle
    sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(9), Inches(0.5))
    tf = sub_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Using Machine Learning"
    p.font.size = Pt(28)
    p.font.color.rgb = COLORS['accent']
    p.alignment = PP_ALIGN.CENTER

    # Bottom info
    info_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.2), Inches(9), Inches(1))
    tf = info_box.text_frame
    p = tf.paragraphs[0]
    p.text = "CAIML Capstone Project  |  REVA University  |  October 2026"
    p.font.size = Pt(16)
    p.font.color.rgb = RGBColor(200, 220, 255)
    p.alignment = PP_ALIGN.CENTER

    # Accent bar at bottom
    add_accent_bar(slide, prs, Inches(7.35), Inches(0.15))

    return slide


def create_team_slide(prs):
    """Slide 2: Professional team introduction."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # White background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header bar
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()

    add_accent_bar(slide, prs, Inches(1.2))

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(9), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "PROJECT TEAM"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Team members in cards
    members = [
        ("Nitin G A", "R23EJ088", "Module 2"),
        ("R Koushik", "R23EJ096", "Module 1"),
        ("S Varshith Sai", "R23EJ100", "Module 2"),
        ("Bhimisetty Karthik", "R23EJ168", "Module 1"),
        ("G M Chandrashekar", "R23EQ029", "Module 2"),
    ]

    start_x = Inches(0.3)
    y = Inches(1.8)
    card_width = Inches(1.85)
    card_height = Inches(1.4)
    gap = Inches(0.1)

    for i, (name, roll, module) in enumerate(members):
        x = start_x + i * (card_width + gap)

        # Card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, card_width, card_height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLORS['white']
        card.line.color.rgb = RGBColor(220, 220, 220)

        # Module badge
        badge_color = COLORS['secondary'] if "1" in module else COLORS['success']
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.1), y + Inches(0.1), Inches(0.7), Inches(0.25))
        badge.fill.solid()
        badge.fill.fore_color.rgb = badge_color
        badge.line.fill.background()

        badge_txt = slide.shapes.add_textbox(x + Inches(0.1), y + Inches(0.1), Inches(0.7), Inches(0.25))
        tf = badge_txt.text_frame
        p = tf.paragraphs[0]
        p.text = module
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER

        # Name
        name_box = slide.shapes.add_textbox(x, y + Inches(0.5), card_width, Inches(0.4))
        tf = name_box.text_frame
        p = tf.paragraphs[0]
        p.text = name
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLORS['dark']
        p.alignment = PP_ALIGN.CENTER

        # Roll
        roll_box = slide.shapes.add_textbox(x, y + Inches(0.9), card_width, Inches(0.3))
        tf = roll_box.text_frame
        p = tf.paragraphs[0]
        p.text = roll
        p.font.size = Pt(10)
        p.font.color.rgb = COLORS['text']
        p.alignment = PP_ALIGN.CENTER

    # Faculty section
    faculty_y = Inches(3.5)

    guide_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), faculty_y, Inches(3.8), Inches(1))
    guide_box.fill.solid()
    guide_box.fill.fore_color.rgb = COLORS['white']
    guide_box.line.color.rgb = RGBColor(220, 220, 220)

    guide_txt = slide.shapes.add_textbox(Inches(1), faculty_y + Inches(0.2), Inches(3.8), Inches(0.4))
    tf = guide_txt.text_frame
    p = tf.paragraphs[0]
    p.text = "Faculty Guide"
    p.font.size = Pt(11)
    p.font.color.rgb = COLORS['text']
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "Ms. Indhuja Balakrishnan"
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = COLORS['primary']
    p2.alignment = PP_ALIGN.CENTER

    lead_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.2), faculty_y, Inches(3.8), Inches(1))
    lead_box.fill.solid()
    lead_box.fill.fore_color.rgb = COLORS['white']
    lead_box.line.color.rgb = RGBColor(220, 220, 220)

    lead_txt = slide.shapes.add_textbox(Inches(5.2), faculty_y + Inches(0.2), Inches(3.8), Inches(0.4))
    tf = lead_txt.text_frame
    p = tf.paragraphs[0]
    p.text = "Center Lead"
    p.font.size = Pt(11)
    p.font.color.rgb = COLORS['text']
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "Dr. M. Shobha Rani"
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = COLORS['primary']
    p2.alignment = PP_ALIGN.CENTER

    # School info
    school_box = slide.shapes.add_textbox(Inches(0.5), Inches(5), Inches(9), Inches(0.8))
    tf = school_box.text_frame
    p = tf.paragraphs[0]
    p.text = "School of Computer Science and Engineering"
    p.font.size = Pt(16)
    p.font.color.rgb = COLORS['primary']
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "B.Tech CSE (AI & ML)  |  Semester VII"
    p2.font.size = Pt(14)
    p2.font.color.rgb = COLORS['text']
    p2.alignment = PP_ALIGN.CENTER

    # Module legend at bottom
    legend_y = Inches(6.3)

    m1_dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(3), legend_y, Inches(0.15), Inches(0.15))
    m1_dot.fill.solid()
    m1_dot.fill.fore_color.rgb = COLORS['secondary']
    m1_dot.line.fill.background()

    m1_txt = slide.shapes.add_textbox(Inches(3.2), legend_y - Inches(0.02), Inches(1.5), Inches(0.2))
    tf = m1_txt.text_frame
    p = tf.paragraphs[0]
    p.text = "Module 1: Prediction"
    p.font.size = Pt(10)
    p.font.color.rgb = COLORS['text']

    m2_dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.2), legend_y, Inches(0.15), Inches(0.15))
    m2_dot.fill.solid()
    m2_dot.fill.fore_color.rgb = COLORS['success']
    m2_dot.line.fill.background()

    m2_txt = slide.shapes.add_textbox(Inches(5.4), legend_y - Inches(0.02), Inches(1.5), Inches(0.2))
    tf = m2_txt.text_frame
    p = tf.paragraphs[0]
    p.text = "Module 2: Risk Mapping"
    p.font.size = Pt(10)
    p.font.color.rgb = COLORS['text']

    return slide


def create_problem_slide(prs):
    """Slide 3: Problem statement with impact metrics."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(1.2))

    # Section number
    num_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(0.5), Inches(0.5))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = "01"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "PROBLEM STATEMENT"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Alarming stats row
    stats_y = Inches(1.6)
    add_metric_box(slide, Inches(0.5), stats_y, Inches(2.2), Inches(1.1), "52", "Taluks Over-exploited", COLORS['danger'])
    add_metric_box(slide, Inches(2.9), stats_y, Inches(2.2), Inches(1.1), "10", "Taluks Critical", COLORS['warning'])
    add_metric_box(slide, Inches(5.3), stats_y, Inches(2.2), Inches(1.1), "27%", "At High Risk", COLORS['accent'])
    add_metric_box(slide, Inches(7.7), stats_y, Inches(2.0), Inches(1.1), "0", "Predictive Systems", COLORS['dark'])

    # Problem description
    prob_box = slide.shapes.add_textbox(Inches(0.5), Inches(3), Inches(9), Inches(2.5))
    tf = prob_box.text_frame
    tf.word_wrap = True

    problems = [
        ("The Challenge", "Groundwater is depleting faster than recharge in Karnataka"),
        ("Current State", "Monitoring is manual, reactive, and district-level only"),
        ("Gap", "No system predicts future trends or identifies risk zones"),
        ("Impact", "Farmers and planners cannot prepare for water scarcity"),
    ]

    for i, (title, desc) in enumerate(problems):
        if i > 0:
            p = tf.add_paragraph()
            p.text = ""
            p.space_before = Pt(6)

        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        p.text = f"{title}:"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLORS['primary']

        p2 = tf.add_paragraph()
        p2.text = f"   {desc}"
        p2.font.size = Pt(14)
        p2.font.color.rgb = COLORS['text']

    # Solution preview box
    sol_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(5.4), Inches(9), Inches(1.3))
    sol_box.fill.solid()
    sol_box.fill.fore_color.rgb = COLORS['primary']
    sol_box.line.fill.background()

    sol_txt = slide.shapes.add_textbox(Inches(0.7), Inches(5.5), Inches(8.6), Inches(1.1))
    tf = sol_txt.text_frame
    p = tf.paragraphs[0]
    p.text = "Our Solution"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    p2 = tf.add_paragraph()
    p2.text = "ML-based prediction + AHP risk mapping + Interactive dashboard for proactive water management"
    p2.font.size = Pt(14)
    p2.font.color.rgb = COLORS['white']

    return slide


def create_solution_slide(prs):
    """Slide 4: Two-module solution architecture."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(1.2))

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(9), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "PROPOSED SOLUTION"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Module 1 card
    m1_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(1.6), Inches(4.5), Inches(3.2))
    m1_box.fill.solid()
    m1_box.fill.fore_color.rgb = COLORS['white']
    m1_box.line.color.rgb = COLORS['secondary']
    m1_box.line.width = Pt(3)

    m1_header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.3), Inches(1.6), Inches(4.5), Inches(0.6))
    m1_header.fill.solid()
    m1_header.fill.fore_color.rgb = COLORS['secondary']
    m1_header.line.fill.background()

    m1_title = slide.shapes.add_textbox(Inches(0.5), Inches(1.7), Inches(4), Inches(0.5))
    tf = m1_title.text_frame
    p = tf.paragraphs[0]
    p.text = "MODULE 1: GWL Prediction"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    m1_content = slide.shapes.add_textbox(Inches(0.5), Inches(2.4), Inches(4.1), Inches(2.2))
    tf = m1_content.text_frame
    tf.word_wrap = True
    items = [
        "Random Forest Regressor",
        "XGBoost Regressor",
        "Support Vector Regressor",
        "Chronological train/val/test split",
        "RMSE, MAE, R² evaluation",
        "Auto-select best model"
    ]
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"  {item}"
        p.font.size = Pt(13)
        p.font.color.rgb = COLORS['text']
        p.space_after = Pt(4)

    # Module 2 card
    m2_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.2), Inches(1.6), Inches(4.5), Inches(3.2))
    m2_box.fill.solid()
    m2_box.fill.fore_color.rgb = COLORS['white']
    m2_box.line.color.rgb = COLORS['success']
    m2_box.line.width = Pt(3)

    m2_header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.2), Inches(1.6), Inches(4.5), Inches(0.6))
    m2_header.fill.solid()
    m2_header.fill.fore_color.rgb = COLORS['success']
    m2_header.line.fill.background()

    m2_title = slide.shapes.add_textbox(Inches(5.4), Inches(1.7), Inches(4), Inches(0.5))
    tf = m2_title.text_frame
    p = tf.paragraphs[0]
    p.text = "MODULE 2: Risk Mapping"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    m2_content = slide.shapes.add_textbox(Inches(5.4), Inches(2.4), Inches(4.1), Inches(2.2))
    tf = m2_content.text_frame
    tf.word_wrap = True
    items = [
        "AHP weight calculation",
        "5 risk indicators",
        "Consistency ratio validation",
        "Jenks Natural Breaks",
        "4 risk classes",
        "CGWB category validation"
    ]
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"  {item}"
        p.font.size = Pt(13)
        p.font.color.rgb = COLORS['text']
        p.space_after = Pt(4)

    # Arrow connecting
    arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.5), Inches(3), Inches(0.9), Inches(0.4))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = COLORS['accent']
    arrow.line.fill.background()

    # Dashboard section
    dash_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(5.1), Inches(9.4), Inches(1.5))
    dash_box.fill.solid()
    dash_box.fill.fore_color.rgb = COLORS['primary']
    dash_box.line.fill.background()

    dash_title = slide.shapes.add_textbox(Inches(0.5), Inches(5.2), Inches(9), Inches(0.4))
    tf = dash_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Interactive Dashboard (Streamlit + Plotly)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    dash_content = slide.shapes.add_textbox(Inches(0.5), Inches(5.7), Inches(9), Inches(0.8))
    tf = dash_content.text_frame
    p = tf.paragraphs[0]
    p.text = "Real-time visualization  |  Model comparison  |  Risk distribution  |  District-level analysis"
    p.font.size = Pt(14)
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER

    return slide


def create_literature_slide(prs):
    """Slide 5: Literature review summary."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(1.2))

    num_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(0.5), Inches(0.5))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = "02"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "LITERATURE REVIEW"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Stats
    add_metric_box(slide, Inches(0.5), Inches(1.6), Inches(2.9), Inches(1), "20+", "Papers Reviewed", COLORS['secondary'])
    add_metric_box(slide, Inches(3.55), Inches(1.6), Inches(2.9), Inches(1), "2017-26", "Publication Range", COLORS['success'])
    add_metric_box(slide, Inches(6.6), Inches(1.6), Inches(2.9), Inches(1), "4", "Research Gaps", COLORS['accent'])

    # Key studies
    studies_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.9), Inches(9), Inches(2))
    tf = studies_box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Key Studies"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLORS['primary']

    studies = [
        ("Wunsch et al. (2021)", "LSTM for GWL forecasting in Germany - achieved state-of-the-art accuracy"),
        ("Asoka et al. (2017)", "Separated monsoon vs pumping effects on Indian groundwater decline"),
        ("Supreetha et al.", "Lion Algorithm + LSTM hybrid for Udupi district prediction"),
    ]

    for author, desc in studies:
        p = tf.add_paragraph()
        p.text = f"  {author}: {desc}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLORS['text']
        p.space_before = Pt(6)

    # Research gaps box
    gap_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(5), Inches(9), Inches(1.7))
    gap_box.fill.solid()
    gap_box.fill.fore_color.rgb = COLORS['white']
    gap_box.line.color.rgb = COLORS['danger']
    gap_box.line.width = Pt(2)

    gap_title = slide.shapes.add_textbox(Inches(0.7), Inches(5.1), Inches(8.6), Inches(0.4))
    tf = gap_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Research Gaps Identified"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLORS['danger']

    gap_content = slide.shapes.add_textbox(Inches(0.7), Inches(5.5), Inches(8.6), Inches(1.1))
    tf = gap_content.text_frame
    gaps = [
        "No statewide Karnataka prediction system",
        "Spatial relationships between wells ignored",
        "Prediction and risk mapping done separately",
        "No real-time dashboard for planners"
    ]
    for i, gap in enumerate(gaps):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"  {gap}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLORS['text']

    return slide


def create_dataset_slide(prs):
    """Slide 6: Dataset with impressive stats."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(1.2))

    num_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(0.5), Inches(0.5))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = "03"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "DATASET COLLECTION"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Impressive stats row
    add_metric_box(slide, Inches(0.3), Inches(1.6), Inches(2.3), Inches(1.2), "123,391", "Total Records", COLORS['primary'])
    add_metric_box(slide, Inches(2.7), Inches(1.6), Inches(2.3), Inches(1.2), "33", "Districts", COLORS['secondary'])
    add_metric_box(slide, Inches(5.1), Inches(1.6), Inches(2.3), Inches(1.2), "2,769", "Stations", COLORS['success'])
    add_metric_box(slide, Inches(7.5), Inches(1.6), Inches(2.3), Inches(1.2), "28", "Years (1996-2024)", COLORS['accent'])

    # Data source
    source_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(3.1), Inches(4.5), Inches(2))
    source_box.fill.solid()
    source_box.fill.fore_color.rgb = COLORS['white']
    source_box.line.color.rgb = RGBColor(220, 220, 220)

    source_title = slide.shapes.add_textbox(Inches(0.5), Inches(3.2), Inches(4.1), Inches(0.4))
    tf = source_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Groundwater Level Data"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLORS['primary']

    source_content = slide.shapes.add_textbox(Inches(0.5), Inches(3.6), Inches(4.1), Inches(1.4))
    tf = source_content.text_frame
    items = [
        "Source: CGWB via NWDP",
        "Frequency: Quarterly (Jan/May/Aug/Nov)",
        "Measurement: Depth to water table (m)",
        "Coverage: All Karnataka districts"
    ]
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"  {item}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLORS['text']

    # Extraction data
    ext_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.2), Inches(3.1), Inches(4.5), Inches(2))
    ext_box.fill.solid()
    ext_box.fill.fore_color.rgb = COLORS['white']
    ext_box.line.color.rgb = RGBColor(220, 220, 220)

    ext_title = slide.shapes.add_textbox(Inches(5.4), Inches(3.2), Inches(4.1), Inches(0.4))
    tf = ext_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Extraction Data (CGWB 2020)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLORS['success']

    ext_content = slide.shapes.add_textbox(Inches(5.4), Inches(3.6), Inches(4.1), Inches(1.4))
    tf = ext_content.text_frame
    items = [
        "227 taluks assessed",
        "Recharge & extraction volumes",
        "Stage of extraction (%)",
        "CGWB categorization status"
    ]
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"  {item}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLORS['text']

    # Features list
    feat_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(5.3), Inches(9.4), Inches(1.4))
    feat_box.fill.solid()
    feat_box.fill.fore_color.rgb = COLORS['primary']
    feat_box.line.fill.background()

    feat_title = slide.shapes.add_textbox(Inches(0.5), Inches(5.4), Inches(9), Inches(0.3))
    tf = feat_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Key Features Extracted"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    feat_content = slide.shapes.add_textbox(Inches(0.5), Inches(5.8), Inches(9), Inches(0.8))
    tf = feat_content.text_frame
    p = tf.paragraphs[0]
    p.text = "Station ID  |  District  |  Tehsil  |  Lat/Long  |  Elevation  |  Date  |  GWL (meters)"
    p.font.size = Pt(12)
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER

    return slide


def create_preprocessing_slide(prs):
    """Slide 7: Data preprocessing steps."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(1.2))

    num_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(0.5), Inches(0.5))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = "04"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "DATA PREPROCESSING"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Process steps as cards
    steps = [
        ("1", "Date Parsing", "Converted datetime\nExtracted Year/Month/Quarter", COLORS['secondary']),
        ("2", "Outlier Removal", "Removed 241 invalid\nrecords (GWL < 0 or > 100m)", COLORS['danger']),
        ("3", "Feature Engineering", "Lag features (1-4 quarters)\nRolling mean/std", COLORS['success']),
        ("4", "Clean Dataset", "123,391 records\nready for ML", COLORS['primary']),
    ]

    x_start = Inches(0.3)
    card_width = Inches(2.3)
    card_height = Inches(2.2)
    gap = Inches(0.15)
    y = Inches(1.6)

    for i, (num, title, desc, color) in enumerate(steps):
        x = x_start + i * (card_width + gap)

        # Card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, card_width, card_height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLORS['white']
        card.line.color.rgb = color
        card.line.width = Pt(2)

        # Number circle
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.85), y + Inches(0.15), Inches(0.5), Inches(0.5))
        circle.fill.solid()
        circle.fill.fore_color.rgb = color
        circle.line.fill.background()

        num_txt = slide.shapes.add_textbox(x + Inches(0.85), y + Inches(0.2), Inches(0.5), Inches(0.4))
        tf = num_txt.text_frame
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER

        # Title
        title_txt = slide.shapes.add_textbox(x + Inches(0.1), y + Inches(0.75), card_width - Inches(0.2), Inches(0.4))
        tf = title_txt.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = color
        p.alignment = PP_ALIGN.CENTER

        # Description
        desc_txt = slide.shapes.add_textbox(x + Inches(0.1), y + Inches(1.15), card_width - Inches(0.2), Inches(1))
        tf = desc_txt.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(10)
        p.font.color.rgb = COLORS['text']
        p.alignment = PP_ALIGN.CENTER

    # Arrows between cards
    for i in range(3):
        x = x_start + (i + 1) * (card_width + gap) - gap - Inches(0.15)
        arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x, y + Inches(1), Inches(0.3), Inches(0.2))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = COLORS['accent']
        arrow.line.fill.background()

    # ML features box
    ml_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(4.1), Inches(9.4), Inches(2.5))
    ml_box.fill.solid()
    ml_box.fill.fore_color.rgb = COLORS['white']
    ml_box.line.color.rgb = RGBColor(220, 220, 220)

    ml_title = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(9), Inches(0.4))
    tf = ml_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Engineered ML Features"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLORS['primary']

    # Feature columns
    col1_txt = slide.shapes.add_textbox(Inches(0.5), Inches(4.7), Inches(4.5), Inches(1.8))
    tf = col1_txt.text_frame
    features1 = [
        "GWL_lag1, GWL_lag2, GWL_lag3, GWL_lag4",
        "GWL_rolling_mean (past 4 quarters)",
        "GWL_rolling_std (variability)",
    ]
    for i, f in enumerate(features1):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"  {f}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLORS['text']

    col2_txt = slide.shapes.add_textbox(Inches(5), Inches(4.7), Inches(4.5), Inches(1.8))
    tf = col2_txt.text_frame
    features2 = [
        "sin_month, cos_month (seasonal)",
        "Latitude, Longitude",
        "target_gwl (next quarter prediction)",
    ]
    for i, f in enumerate(features2):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"  {f}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLORS['text']

    return slide


def create_eda_slide(prs, title, image_path, insight, plot_num):
    """Create an EDA visualization slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.9))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(0.9), Inches(0.1))

    num_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.2), Inches(0.5), Inches(0.5))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = "05"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.22), Inches(8), Inches(0.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"EDA: {title}"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Plot number badge
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9), Inches(0.2), Inches(0.7), Inches(0.5))
    badge.fill.solid()
    badge.fill.fore_color.rgb = COLORS['accent']
    badge.line.fill.background()

    badge_txt = slide.shapes.add_textbox(Inches(9), Inches(0.25), Inches(0.7), Inches(0.4))
    tf = badge_txt.text_frame
    p = tf.paragraphs[0]
    p.text = f"{plot_num}/5"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER

    # Image
    if Path(image_path).exists():
        slide.shapes.add_picture(str(image_path), Inches(0.3), Inches(1.1), width=Inches(9.4), height=Inches(5))

    # Insight box at bottom
    insight_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(6.2), Inches(9.4), Inches(0.6))
    insight_box.fill.solid()
    insight_box.fill.fore_color.rgb = COLORS['primary']
    insight_box.line.fill.background()

    insight_txt = slide.shapes.add_textbox(Inches(0.5), Inches(6.3), Inches(9), Inches(0.4))
    tf = insight_txt.text_frame
    p = tf.paragraphs[0]
    p.text = f"Insight: {insight}"
    p.font.size = Pt(13)
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER

    return slide


def create_ml_selection_slide(prs):
    """Slide: ML Algorithm Selection."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(1.2))

    num_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(0.5), Inches(0.5))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = "06"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "ML ALGORITHM SELECTION"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Algorithm cards
    algorithms = [
        ("Random Forest", "Ensemble of decision trees", ["Non-linear relationships", "Robust to outliers", "Feature importance"], COLORS['secondary']),
        ("XGBoost", "Gradient boosting framework", ["State-of-the-art accuracy", "Regularization", "Handles missing values"], COLORS['success']),
        ("SVR", "Support Vector Regression", ["Works with RBF kernel", "Effective for smaller data", "Good baseline"], COLORS['accent']),
    ]

    x_start = Inches(0.3)
    card_width = Inches(3.1)
    card_height = Inches(2.8)
    gap = Inches(0.2)
    y = Inches(1.5)

    for i, (name, desc, points, color) in enumerate(algorithms):
        x = x_start + i * (card_width + gap)

        # Card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, card_width, card_height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLORS['white']
        card.line.color.rgb = color
        card.line.width = Pt(3)

        # Header stripe
        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, card_width, Inches(0.5))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = color
        stripe.line.fill.background()

        # Name
        name_txt = slide.shapes.add_textbox(x, y + Inches(0.08), card_width, Inches(0.4))
        tf = name_txt.text_frame
        p = tf.paragraphs[0]
        p.text = name
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER

        # Description
        desc_txt = slide.shapes.add_textbox(x + Inches(0.15), y + Inches(0.6), card_width - Inches(0.3), Inches(0.4))
        tf = desc_txt.text_frame
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(10)
        p.font.italic = True
        p.font.color.rgb = COLORS['text']
        p.alignment = PP_ALIGN.CENTER

        # Points
        points_txt = slide.shapes.add_textbox(x + Inches(0.15), y + Inches(1.1), card_width - Inches(0.3), Inches(1.5))
        tf = points_txt.text_frame
        for j, point in enumerate(points):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"  {point}"
            p.font.size = Pt(11)
            p.font.color.rgb = COLORS['text']

    # Why these section
    why_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(4.5), Inches(9.4), Inches(2.2))
    why_box.fill.solid()
    why_box.fill.fore_color.rgb = COLORS['primary']
    why_box.line.fill.background()

    why_title = slide.shapes.add_textbox(Inches(0.5), Inches(4.6), Inches(9), Inches(0.4))
    tf = why_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Why These Algorithms?"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    why_content = slide.shapes.add_textbox(Inches(0.5), Inches(5.1), Inches(9), Inches(1.5))
    tf = why_content.text_frame
    reasons = [
        "Literature shows these perform best for groundwater prediction",
        "Ensemble approach: compare multiple models, select best on validation RMSE",
        "XGBoost consistently outperforms in structured/tabular data competitions",
        "RF provides interpretable feature importance for domain validation"
    ]
    for i, r in enumerate(reasons):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"  {r}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLORS['white']

    return slide


def create_implementation_slide(prs):
    """Slide: Model Implementation with code."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(1.2))

    num_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(0.5), Inches(0.5))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = "07"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "MODEL IMPLEMENTATION"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Code box
    code_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(1.5), Inches(9.4), Inches(5.2))
    code_bg.fill.solid()
    code_bg.fill.fore_color.rgb = RGBColor(30, 30, 30)
    code_bg.line.color.rgb = RGBColor(60, 60, 60)

    # File name tab
    tab = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(1.3), Inches(1.8), Inches(0.35))
    tab.fill.solid()
    tab.fill.fore_color.rgb = RGBColor(50, 50, 50)
    tab.line.fill.background()

    tab_txt = slide.shapes.add_textbox(Inches(0.4), Inches(1.35), Inches(1.6), Inches(0.3))
    tf = tab_txt.text_frame
    p = tf.paragraphs[0]
    p.text = "pipeline.py"
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(180, 180, 180)

    code = """# Train all models
def _train_all_models(X_train, y_train):
    models = {}

    # Random Forest
    models['rf'] = RandomForestRegressor(
        n_estimators=200, random_state=0, n_jobs=-1
    )
    models['rf'].fit(X_train, y_train)

    # XGBoost
    models['xgboost'] = xgb.XGBRegressor(
        n_estimators=300, learning_rate=0.05, max_depth=6
    )
    models['xgboost'].fit(X_train, y_train)

    # SVR (subset for speed)
    models['svr'] = SVR(kernel='rbf', C=10)
    models['svr'].fit(X_train[:5000], y_train[:5000])

    return models

# Evaluate and select best
val_metrics = {name: _evaluate(m, X_val, y_val) for name, m in models.items()}
best_model = min(val_metrics, key=lambda k: val_metrics[k]["rmse"])"""

    code_txt = slide.shapes.add_textbox(Inches(0.5), Inches(1.7), Inches(9), Inches(5))
    tf = code_txt.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = code
    p.font.size = Pt(11)
    p.font.name = 'Courier New'
    p.font.color.rgb = RGBColor(220, 220, 220)

    return slide


def create_evaluation_slide(prs):
    """Slide: Model Evaluation Results."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(1.2))

    num_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(0.5), Inches(0.5))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = "08"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "MODEL EVALUATION"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Results table header
    table_y = Inches(1.6)
    header_row = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), table_y, Inches(9), Inches(0.5))
    header_row.fill.solid()
    header_row.fill.fore_color.rgb = COLORS['primary']
    header_row.line.fill.background()

    headers = ["Model", "RMSE", "MAE", "R²", "Status"]
    col_widths = [Inches(2.5), Inches(1.5), Inches(1.5), Inches(1.5), Inches(2)]
    col_x = Inches(0.5)

    for i, h in enumerate(headers):
        txt = slide.shapes.add_textbox(col_x, table_y + Inches(0.1), col_widths[i], Inches(0.4))
        tf = txt.text_frame
        p = tf.paragraphs[0]
        p.text = h
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER
        col_x += col_widths[i]

    # Data rows
    data = [
        ("Random Forest", "3.90", "3.21", "0.31", "Good"),
        ("XGBoost", "3.63", "3.01", "0.40", "BEST"),
        ("SVR", "5.01", "4.31", "-0.14", "Baseline"),
    ]

    row_y = table_y + Inches(0.5)
    for row_idx, (model, rmse, mae, r2, status) in enumerate(data):
        # Row background
        row_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), row_y, Inches(9), Inches(0.6))
        if status == "BEST":
            row_bg.fill.solid()
            row_bg.fill.fore_color.rgb = RGBColor(232, 245, 233)
        else:
            row_bg.fill.solid()
            row_bg.fill.fore_color.rgb = COLORS['white']
        row_bg.line.color.rgb = RGBColor(220, 220, 220)

        col_x = Inches(0.5)
        values = [model, rmse, mae, r2, status]
        for i, v in enumerate(values):
            txt = slide.shapes.add_textbox(col_x, row_y + Inches(0.15), col_widths[i], Inches(0.4))
            tf = txt.text_frame
            p = tf.paragraphs[0]
            p.text = v
            p.font.size = Pt(13)
            if status == "BEST" and i == 4:
                p.font.bold = True
                p.font.color.rgb = COLORS['success']
            else:
                p.font.color.rgb = COLORS['text']
            p.alignment = PP_ALIGN.CENTER
            col_x += col_widths[i]

        row_y += Inches(0.6)

    # Winner highlight
    winner_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(4.2), Inches(9), Inches(1.2))
    winner_box.fill.solid()
    winner_box.fill.fore_color.rgb = COLORS['success']
    winner_box.line.fill.background()

    trophy = slide.shapes.add_textbox(Inches(0.7), Inches(4.3), Inches(0.8), Inches(1))
    tf = trophy.text_frame
    p = tf.paragraphs[0]
    p.text = "★"
    p.font.size = Pt(48)
    p.font.color.rgb = COLORS['warning']

    winner_txt = slide.shapes.add_textbox(Inches(1.5), Inches(4.4), Inches(7.8), Inches(1))
    tf = winner_txt.text_frame
    p = tf.paragraphs[0]
    p.text = "Best Model: XGBoost"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    p2 = tf.add_paragraph()
    p2.text = "Lowest RMSE (3.63m) | Highest R² (0.40) | Selected for predictions"
    p2.font.size = Pt(14)
    p2.font.color.rgb = RGBColor(200, 255, 200)

    # Test set results
    test_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(5.6), Inches(9), Inches(1.1))
    test_box.fill.solid()
    test_box.fill.fore_color.rgb = COLORS['white']
    test_box.line.color.rgb = COLORS['primary']
    test_box.line.width = Pt(2)

    test_title = slide.shapes.add_textbox(Inches(0.7), Inches(5.7), Inches(8.6), Inches(0.4))
    tf = test_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Test Set Performance (Final Evaluation)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLORS['primary']

    test_content = slide.shapes.add_textbox(Inches(0.7), Inches(6.1), Inches(8.6), Inches(0.5))
    tf = test_content.text_frame
    p = tf.paragraphs[0]
    p.text = "RMSE: 3.63 meters  |  MAE: 3.01 meters  |  R²: 0.40  |  160 test samples"
    p.font.size = Pt(13)
    p.font.color.rgb = COLORS['text']
    p.alignment = PP_ALIGN.CENTER

    return slide


def create_risk_mapping_slide(prs):
    """Slide: Module 2 Risk Mapping."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header - different color for Module 2
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['success']
    header.line.fill.background()

    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.2), prs.slide_width, Inches(0.15))
    bar.fill.solid()
    bar.fill.fore_color.rgb = COLORS['warning']
    bar.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(9), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "MODULE 2: DEPLETION RISK MAPPING"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # AHP Weights section
    ahp_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(1.6), Inches(4.5), Inches(3))
    ahp_box.fill.solid()
    ahp_box.fill.fore_color.rgb = COLORS['white']
    ahp_box.line.color.rgb = COLORS['success']
    ahp_box.line.width = Pt(2)

    ahp_title = slide.shapes.add_textbox(Inches(0.5), Inches(1.7), Inches(4.1), Inches(0.4))
    tf = ahp_title.text_frame
    p = tf.paragraphs[0]
    p.text = "AHP-Weighted Indicators"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLORS['success']

    # Indicator bars
    indicators = [
        ("Predicted Decline Rate", 0.503, COLORS['danger']),
        ("Current Depth", 0.260, COLORS['warning']),
        ("Variability", 0.134, COLORS['secondary']),
        ("Rainfall Dependence", 0.068, COLORS['primary']),
        ("LULC Change", 0.035, RGBColor(150, 150, 150)),
    ]

    bar_y = Inches(2.2)
    for name, weight, color in indicators:
        # Label
        lbl = slide.shapes.add_textbox(Inches(0.5), bar_y, Inches(2.5), Inches(0.3))
        tf = lbl.text_frame
        p = tf.paragraphs[0]
        p.text = name
        p.font.size = Pt(10)
        p.font.color.rgb = COLORS['text']

        # Bar background
        bar_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), bar_y + Inches(0.3), Inches(3.5), Inches(0.2))
        bar_bg.fill.solid()
        bar_bg.fill.fore_color.rgb = RGBColor(230, 230, 230)
        bar_bg.line.fill.background()

        # Bar fill
        bar_fill = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), bar_y + Inches(0.3), Inches(3.5 * weight / 0.503), Inches(0.2))
        bar_fill.fill.solid()
        bar_fill.fill.fore_color.rgb = color
        bar_fill.line.fill.background()

        # Weight value
        wt = slide.shapes.add_textbox(Inches(4.05), bar_y + Inches(0.25), Inches(0.6), Inches(0.3))
        tf = wt.text_frame
        p = tf.paragraphs[0]
        p.text = f"{weight:.2f}"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLORS['text']

        bar_y += Inches(0.55)

    # Consistency check
    cr_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(4.3), Inches(4.1), Inches(0.4))
    cr_box.fill.solid()
    cr_box.fill.fore_color.rgb = RGBColor(232, 245, 233)
    cr_box.line.fill.background()

    cr_txt = slide.shapes.add_textbox(Inches(0.6), Inches(4.35), Inches(3.9), Inches(0.3))
    tf = cr_txt.text_frame
    p = tf.paragraphs[0]
    p.text = "CR = 0.054 < 0.10 (Consistent)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLORS['success']

    # Risk classes section
    risk_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.2), Inches(1.6), Inches(4.5), Inches(3))
    risk_box.fill.solid()
    risk_box.fill.fore_color.rgb = COLORS['white']
    risk_box.line.color.rgb = COLORS['success']
    risk_box.line.width = Pt(2)

    risk_title = slide.shapes.add_textbox(Inches(5.4), Inches(1.7), Inches(4.1), Inches(0.4))
    tf = risk_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Jenks Risk Classification"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLORS['success']

    # Risk class boxes
    classes = [
        ("Low", "20%", COLORS['success']),
        ("Moderate", "42%", COLORS['secondary']),
        ("High", "28%", COLORS['warning']),
        ("Very High", "10%", COLORS['danger']),
    ]

    class_x = Inches(5.4)
    class_y = Inches(2.3)
    for name, pct, color in classes:
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, class_x, class_y, Inches(2), Inches(0.5))
        box.fill.solid()
        box.fill.fore_color.rgb = color
        box.line.fill.background()

        txt = slide.shapes.add_textbox(class_x, class_y + Inches(0.1), Inches(2), Inches(0.35))
        tf = txt.text_frame
        p = tf.paragraphs[0]
        p.text = f"{name}: {pct}"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER

        class_y += Inches(0.6)

    # Validation section
    val_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(5), Inches(9.4), Inches(1.7))
    val_box.fill.solid()
    val_box.fill.fore_color.rgb = COLORS['primary']
    val_box.line.fill.background()

    val_title = slide.shapes.add_textbox(Inches(0.5), Inches(5.1), Inches(9), Inches(0.4))
    tf = val_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Validation Against CGWB Official Categories"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    val_stats = slide.shapes.add_textbox(Inches(0.5), Inches(5.6), Inches(9), Inches(1))
    tf = val_stats.text_frame
    p = tf.paragraphs[0]
    p.text = "Accuracy: 68%  |  Cohen's Kappa: 0.54 (Moderate Agreement)"
    p.font.size = Pt(14)
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "Compared our risk zones with CGWB's Safe/Semi-critical/Critical/Over-exploited classifications"
    p2.font.size = Pt(12)
    p2.font.color.rgb = RGBColor(200, 220, 255)
    p2.alignment = PP_ALIGN.CENTER

    return slide


def create_demo_slide(prs):
    """Slide: Working Demonstration."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(1.2))

    num_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(0.5), Inches(0.5))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = "09"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "WORKING DEMONSTRATION"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Demo commands
    commands = [
        ("1", "Run Full Pipeline", "python -m src.main", "Trains models, generates predictions, creates risk map"),
        ("2", "Run Test Suite", "python -m tests.test_modules", "13 test cases - all passing"),
        ("3", "Launch Dashboard", "streamlit run dashboard.py", "Opens interactive visualization at localhost:8501"),
        ("4", "Interactive Demo", "python demo_saturday.py", "Step-by-step demo for presentation"),
    ]

    y = Inches(1.6)
    for num, title, cmd, desc in commands:
        # Card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), y, Inches(9.4), Inches(0.9))
        card.fill.solid()
        card.fill.fore_color.rgb = COLORS['white']
        card.line.color.rgb = RGBColor(220, 220, 220)

        # Number
        num_circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.5), y + Inches(0.2), Inches(0.5), Inches(0.5))
        num_circle.fill.solid()
        num_circle.fill.fore_color.rgb = COLORS['primary']
        num_circle.line.fill.background()

        num_txt = slide.shapes.add_textbox(Inches(0.5), y + Inches(0.25), Inches(0.5), Inches(0.4))
        tf = num_txt.text_frame
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER

        # Title
        title_txt = slide.shapes.add_textbox(Inches(1.2), y + Inches(0.1), Inches(3), Inches(0.4))
        tf = title_txt.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLORS['primary']

        # Command
        cmd_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), y + Inches(0.45), Inches(4), Inches(0.35))
        cmd_bg.fill.solid()
        cmd_bg.fill.fore_color.rgb = RGBColor(40, 44, 52)
        cmd_bg.line.fill.background()

        cmd_txt = slide.shapes.add_textbox(Inches(1.3), y + Inches(0.5), Inches(3.8), Inches(0.3))
        tf = cmd_txt.text_frame
        p = tf.paragraphs[0]
        p.text = f"$ {cmd}"
        p.font.size = Pt(11)
        p.font.name = 'Courier New'
        p.font.color.rgb = RGBColor(0, 255, 100)

        # Description
        desc_txt = slide.shapes.add_textbox(Inches(5.5), y + Inches(0.3), Inches(4), Inches(0.4))
        tf = desc_txt.text_frame
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(11)
        p.font.color.rgb = COLORS['text']

        y += Inches(1.05)

    # Outputs section
    out_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(5.9), Inches(9.4), Inches(0.9))
    out_box.fill.solid()
    out_box.fill.fore_color.rgb = COLORS['success']
    out_box.line.fill.background()

    out_title = slide.shapes.add_textbox(Inches(0.5), Inches(6), Inches(9), Inches(0.35))
    tf = out_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Generated Outputs"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    out_content = slide.shapes.add_textbox(Inches(0.5), Inches(6.35), Inches(9), Inches(0.4))
    tf = out_content.text_frame
    p = tf.paragraphs[0]
    p.text = "module1_test_predictions.csv  |  module2_risk_mapping.csv  |  10 EDA plots  |  Dashboard"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(200, 255, 200)
    p.alignment = PP_ALIGN.CENTER

    return slide


def create_conclusion_slide(prs):
    """Slide: Conclusion with achievements."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['light']
    bg.line.fill.background()

    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    add_accent_bar(slide, prs, Inches(1.2))

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(9), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "CONCLUSION"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

    # Achievements
    achievements = [
        ("Data", "123,391 real CGWB groundwater records collected", COLORS['secondary']),
        ("EDA", "10 comprehensive visualization plots generated", COLORS['success']),
        ("Models", "3 ML models trained, XGBoost selected (RMSE: 3.63m)", COLORS['primary']),
        ("Risk Map", "AHP + Jenks classification with 68% CGWB match", COLORS['warning']),
        ("Testing", "13 test cases covering valid/invalid/boundary inputs", COLORS['accent']),
        ("Dashboard", "Interactive Streamlit + Plotly visualization ready", COLORS['danger']),
    ]

    y = Inches(1.6)
    for title, desc, color in achievements:
        # Check mark
        check = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.5), y, Inches(0.4), Inches(0.4))
        check.fill.solid()
        check.fill.fore_color.rgb = color
        check.line.fill.background()

        check_txt = slide.shapes.add_textbox(Inches(0.5), y, Inches(0.4), Inches(0.4))
        tf = check_txt.text_frame
        p = tf.paragraphs[0]
        p.text = "✓"
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER

        # Title badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), y + Inches(0.05), Inches(1.2), Inches(0.3))
        badge.fill.solid()
        badge.fill.fore_color.rgb = color
        badge.line.fill.background()

        badge_txt = slide.shapes.add_textbox(Inches(1.1), y + Inches(0.08), Inches(1.2), Inches(0.25))
        tf = badge_txt.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER

        # Description
        desc_txt = slide.shapes.add_textbox(Inches(2.5), y + Inches(0.05), Inches(7), Inches(0.35))
        tf = desc_txt.text_frame
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(13)
        p.font.color.rgb = COLORS['text']

        y += Inches(0.55)

    # Next steps
    next_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(5), Inches(9.4), Inches(1.7))
    next_box.fill.solid()
    next_box.fill.fore_color.rgb = COLORS['primary']
    next_box.line.fill.background()

    next_title = slide.shapes.add_textbox(Inches(0.5), Inches(5.1), Inches(9), Inches(0.4))
    tf = next_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Future Work"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLORS['accent']

    next_content = slide.shapes.add_textbox(Inches(0.5), Inches(5.6), Inches(9), Inches(1))
    tf = next_content.text_frame
    steps = [
        "Integrate real-time data updates from CGWB portal",
        "Implement spatial interpolation (Kriging) for unmeasured areas",
        "Deploy dashboard for government water resource planners"
    ]
    for i, s in enumerate(steps):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"  {s}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLORS['white']

    return slide


def create_thankyou_slide(prs):
    """Slide: Thank You."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    add_gradient_background(slide, prs, COLORS['primary'], COLORS['secondary'])

    # Accent bar
    add_accent_bar(slide, prs, Inches(7.35), Inches(0.15))

    # Thank you text
    ty_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(1.5))
    tf = ty_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Thank You!"
    p.font.size = Pt(60)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER

    # Questions
    q_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(9), Inches(0.8))
    tf = q_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Questions & Discussion"
    p.font.size = Pt(28)
    p.font.color.rgb = COLORS['accent']
    p.alignment = PP_ALIGN.CENTER

    # Contact
    contact_box = slide.shapes.add_textbox(Inches(0.5), Inches(5.5), Inches(9), Inches(0.8))
    tf = contact_box.text_frame
    p = tf.paragraphs[0]
    p.text = "CAIML_Shobha_Rani_4_PS_160"
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(200, 220, 255)
    p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "School of CSE | REVA University | October 2026"
    p2.font.size = Pt(12)
    p2.font.color.rgb = RGBColor(180, 200, 255)
    p2.alignment = PP_ALIGN.CENTER

    return slide


def create_presentation():
    """Create the impressive presentation."""
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # Create all slides
    create_title_slide(prs)           # 1
    create_team_slide(prs)            # 2
    create_problem_slide(prs)         # 3
    create_solution_slide(prs)        # 4
    create_literature_slide(prs)      # 5
    create_dataset_slide(prs)         # 6
    create_preprocessing_slide(prs)   # 7

    # EDA slides
    eda_slides = [
        ("Groundwater Level Distribution", 'plot1_gwl_distribution.png', "Mean GWL: 7.31m | High variability across districts", 1),
        ("Yearly Trend (1995-2024)", 'plot2_yearly_trend.png', "Gradual deepening of water table over decades", 2),
        ("Seasonal Pattern", 'plot3_seasonal_pattern.png', "Monsoon months show shallower GWL (recovery)", 3),
        ("District Comparison", 'plot4_district_comparison.png', "Higher values indicate deeper (more depleted) groundwater", 4),
        ("CGWB Extraction Categories", 'plot6_extraction_categories.png', "52 over-exploited + 10 critical = 27% at risk", 5),
    ]

    for title, fname, insight, num in eda_slides:
        create_eda_slide(prs, title, PLOTS_DIR / fname, insight, num)  # 8-12

    create_ml_selection_slide(prs)    # 13
    create_implementation_slide(prs)  # 14
    create_evaluation_slide(prs)      # 15
    create_risk_mapping_slide(prs)    # 16
    create_demo_slide(prs)            # 17
    create_conclusion_slide(prs)      # 18
    create_thankyou_slide(prs)        # 19

    # Save
    output_path = OUTPUT_DIR / 'Groundwater_Depletion_Presentation.pptx'
    prs.save(output_path)
    print(f"Presentation saved to: {output_path}")
    print(f"Total slides: {len(prs.slides)}")
    return output_path


if __name__ == '__main__':
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    create_presentation()
