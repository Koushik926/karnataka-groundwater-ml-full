"""
Build PowerPoint Presentation for Saturday Review
Covers all 9 required topics
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pathlib import Path
import os

# Paths
BASE_DIR = Path(__file__).parent.parent
PLOTS_DIR = BASE_DIR / 'outputs' / 'eda_plots'
OUTPUT_DIR = Path(__file__).parent

def add_title_slide(prs, title, subtitle=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

    # Background
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0, 51, 102)
    shape.line.fill.background()

    # Title
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(1.5))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    if subtitle:
        txBox2 = slide.shapes.add_textbox(Inches(0.5), Inches(4), Inches(9), Inches(1))
        tf2 = txBox2.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = subtitle
        p2.font.size = Pt(24)
        p2.font.color.rgb = RGBColor(200, 200, 200)
        p2.alignment = PP_ALIGN.CENTER

    return slide

def add_content_slide(prs, title, bullets, image_path=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

    # Title bar
    title_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1))
    title_shape.fill.solid()
    title_shape.fill.fore_color.rgb = RGBColor(0, 51, 102)
    title_shape.line.fill.background()

    # Title text
    txBox = slide.shapes.add_textbox(Inches(0.3), Inches(0.2), Inches(9), Inches(0.6))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    # Content area
    if image_path and Path(image_path).exists():
        # Left: bullets, Right: image
        content_box = slide.shapes.add_textbox(Inches(0.3), Inches(1.2), Inches(4.5), Inches(5.5))
        tf = content_box.text_frame
        tf.word_wrap = True

        for i, bullet in enumerate(bullets):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"• {bullet}"
            p.font.size = Pt(16)
            p.space_after = Pt(8)

        # Add image
        slide.shapes.add_picture(str(image_path), Inches(5), Inches(1.3), width=Inches(4.7))
    else:
        # Full width bullets
        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9), Inches(5.5))
        tf = content_box.text_frame
        tf.word_wrap = True

        for i, bullet in enumerate(bullets):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"• {bullet}"
            p.font.size = Pt(20)
            p.space_after = Pt(12)

    return slide

def add_image_slide(prs, title, image_path, caption=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title bar
    title_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.8))
    title_shape.fill.solid()
    title_shape.fill.fore_color.rgb = RGBColor(0, 51, 102)
    title_shape.line.fill.background()

    txBox = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(9), Inches(0.5))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    # Image
    if Path(image_path).exists():
        slide.shapes.add_picture(str(image_path), Inches(0.3), Inches(1), width=Inches(9.4))

    # Caption
    if caption:
        cap_box = slide.shapes.add_textbox(Inches(0.3), Inches(6.8), Inches(9), Inches(0.5))
        tf = cap_box.text_frame
        p = tf.paragraphs[0]
        p.text = caption
        p.font.size = Pt(14)
        p.font.italic = True
        p.alignment = PP_ALIGN.CENTER

    return slide

def add_code_slide(prs, title, code_text):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title bar
    title_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.8))
    title_shape.fill.solid()
    title_shape.fill.fore_color.rgb = RGBColor(0, 51, 102)
    title_shape.line.fill.background()

    txBox = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(9), Inches(0.5))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    # Code box
    code_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.3), Inches(1), Inches(9.4), Inches(5.7))
    code_shape.fill.solid()
    code_shape.fill.fore_color.rgb = RGBColor(40, 44, 52)

    code_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.1), Inches(9), Inches(5.5))
    tf = code_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = code_text
    p.font.size = Pt(11)
    p.font.name = 'Courier New'
    p.font.color.rgb = RGBColor(220, 220, 220)

    return slide

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # =============================================
    # SLIDE 1: Title
    # =============================================
    add_title_slide(prs,
        "Spatio-Temporal Prediction and Risk Mapping\nof Groundwater Depletion in Karnataka",
        "CAIML_Shobha_Rani_4_PS_160 | REVA University | October 2026")

    # =============================================
    # SLIDE 2: Team
    # =============================================
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1))
    title_shape.fill.solid()
    title_shape.fill.fore_color.rgb = RGBColor(0, 51, 102)
    title_shape.line.fill.background()

    txBox = slide.shapes.add_textbox(Inches(0.3), Inches(0.2), Inches(9), Inches(0.6))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "Project Team"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    team_info = """
    Team Members:
    1. NITIN G A (R23EJ088)
    2. R KOUSHIK (R23EJ096)
    3. S VARSHITH SAI (R23EJ100)
    4. BHIMISETTY KARTHIK (R23EJ168)
    5. G M CHANDRASHEKAR (R23EQ029)

    Faculty Guide: Ms Indhuja Balakrishnan
    Center Lead: Dr. M. Shobha Rani

    School of Computer Science and Engineering
    Semester VII
    """
    content_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5))
    tf = content_box.text_frame
    p = tf.paragraphs[0]
    p.text = team_info
    p.font.size = Pt(20)

    # =============================================
    # SLIDE 3: Problem Statement
    # =============================================
    add_content_slide(prs, "1. Problem Statement", [
        "Groundwater depletion is a critical issue in Karnataka",
        "52 taluks are over-exploited, 10 are critical (CGWB 2020)",
        "Current monitoring is manual and reactive",
        "No predictive system for future groundwater trends",
        "",
        "OBJECTIVES:",
        "• Predict groundwater level trends using ML models",
        "• Identify high-risk depletion zones",
        "• Build an interactive dashboard for visualization",
        "• Support sustainable water resource planning"
    ])

    # =============================================
    # SLIDE 4: Proposed Solution
    # =============================================
    add_content_slide(prs, "Proposed Solution", [
        "Module 1: Groundwater Level Prediction",
        "  - Train ML models (RF, XGBoost, SVR, LSTM)",
        "  - Predict future groundwater depths",
        "  - Explain predictions using SHAP",
        "",
        "Module 2: Depletion Risk Mapping",
        "  - AHP-weighted risk indicators",
        "  - Jenks Natural Breaks classification",
        "  - 4 risk zones: Low, Moderate, High, Very High",
        "",
        "Interactive Streamlit Dashboard",
        "  - Visualize predictions and risk maps",
        "  - District and taluk-level analysis"
    ])

    # =============================================
    # SLIDE 5: Literature Review
    # =============================================
    add_content_slide(prs, "2. Literature Review", [
        "Reviewed 20 peer-reviewed papers (2017-2026)",
        "",
        "Key Studies:",
        "• Wunsch et al. (2021) - LSTM for GWL forecasting in Germany",
        "• Asoka et al. (2017) - Monsoon vs pumping effects in India",
        "• Supreetha et al. - Lion Algorithm + LSTM for Udupi district",
        "",
        "Research Gap Identified:",
        "• No statewide Karnataka prediction system exists",
        "• Spatial relationships between wells ignored",
        "• Prediction and risk mapping done separately",
        "• No real-time dashboard for planners"
    ])

    # =============================================
    # SLIDE 6: Dataset Collection
    # =============================================
    add_content_slide(prs, "3. Dataset Collection", [
        "Source: CGWB via National Water Data Portal (NWDP)",
        "",
        "Groundwater Level Data:",
        "• Total Records: 123,391",
        "• Time Period: 1996 - 2024 (28 years)",
        "• Districts Covered: 33",
        "• Monitoring Stations: 2,769",
        "• Quarterly measurements (Jan, May, Aug, Nov)",
        "",
        "Extraction Data (CGWB 2020):",
        "• 227 taluks with recharge/extraction figures",
        "• Includes CGWB categorization (Safe to Over-exploited)"
    ], PLOTS_DIR / 'plot9_stations_map.png')

    # =============================================
    # SLIDE 7: Dataset Features
    # =============================================
    add_content_slide(prs, "Dataset Features", [
        "GWL Dataset Columns (21 features):",
        "• Station ID, Agency (CGWB)",
        "• State, District, Tehsil, Block, Village",
        "• Latitude, Longitude, Elevation (RL_MSL)",
        "• Date (Data Acquisition Time)",
        "• Groundwater Level (meters below ground)",
        "",
        "Extraction Dataset Columns (16 features):",
        "• District, Taluk",
        "• Monsoon/Non-monsoon recharge",
        "• Total recharge, Extractable resource",
        "• Irrigation & domestic extraction",
        "• Stage of extraction (%)",
        "• CGWB Categorization"
    ])

    # =============================================
    # SLIDE 8: Data Preprocessing
    # =============================================
    add_content_slide(prs, "4. Data Preprocessing", [
        "Steps Applied:",
        "",
        "1. Date Parsing:",
        "   • Converted 'Data Acquisition Time' to datetime",
        "   • Extracted Year, Month, Quarter",
        "",
        "2. Outlier Removal:",
        "   • Removed 241 records with GWL < 0 or > 100m",
        "",
        "3. Missing Value Handling:",
        "   • 0 missing GWL values after cleaning",
        "   • Dropped rows with missing District/Date",
        "",
        "4. Clean Dataset: 123,391 records ready for analysis"
    ], PLOTS_DIR / 'plot10_data_quality.png')

    # =============================================
    # SLIDE 9: EDA - Distribution
    # =============================================
    add_image_slide(prs, "5. EDA: Groundwater Level Distribution",
                   PLOTS_DIR / 'plot1_gwl_distribution.png',
                   "Mean GWL: 7.31m | Std: 6.73m | Range: 0 - 92.5m")

    # =============================================
    # SLIDE 10: EDA - Yearly Trend
    # =============================================
    add_image_slide(prs, "EDA: Yearly Trend (1995-2024)",
                   PLOTS_DIR / 'plot2_yearly_trend.png',
                   "Observation: Gradual deepening of water table over decades")

    # =============================================
    # SLIDE 11: EDA - Seasonal Pattern
    # =============================================
    add_image_slide(prs, "EDA: Seasonal Pattern",
                   PLOTS_DIR / 'plot3_seasonal_pattern.png',
                   "Green bars = Monsoon months (Jun-Oct) showing shallower GWL")

    # =============================================
    # SLIDE 12: EDA - District Comparison
    # =============================================
    add_image_slide(prs, "EDA: District-wise Analysis",
                   PLOTS_DIR / 'plot4_district_comparison.png',
                   "Higher values indicate deeper (more depleted) groundwater")

    # =============================================
    # SLIDE 13: EDA - Extraction Categories
    # =============================================
    add_image_slide(prs, "EDA: CGWB Extraction Categories",
                   PLOTS_DIR / 'plot6_extraction_categories.png',
                   "52 taluks over-exploited + 10 critical = 27% at risk")

    # =============================================
    # SLIDE 14: ML Algorithm Selection
    # =============================================
    add_content_slide(prs, "6. ML Algorithm Selection", [
        "Selected Algorithms:",
        "",
        "1. Random Forest Regressor",
        "   • Handles non-linear relationships",
        "   • Robust to outliers, no scaling needed",
        "",
        "2. XGBoost Regressor",
        "   • Gradient boosting with regularization",
        "   • Best performance on structured data",
        "",
        "3. Support Vector Regressor (SVR)",
        "   • Effective for small-medium datasets",
        "   • RBF kernel for non-linearity",
        "",
        "4. LSTM (scaffolded)",
        "   • For sequential time-series patterns"
    ])

    # =============================================
    # SLIDE 15: Why These Algorithms
    # =============================================
    add_content_slide(prs, "Why These Algorithms?", [
        "Random Forest:",
        "• Literature shows RF performs well for GWL prediction",
        "• Feature importance for interpretability",
        "",
        "XGBoost:",
        "• State-of-the-art for tabular data",
        "• Handles missing values internally",
        "• Regularization prevents overfitting",
        "",
        "SVR:",
        "• Good baseline for comparison",
        "• Works with limited training data",
        "",
        "Ensemble Approach:",
        "• Compare models, select best on validation RMSE"
    ])

    # =============================================
    # SLIDE 16: Model Implementation
    # =============================================
    code = """# Model Training Pipeline (pipeline.py)

def _fit_random_forest(X, y):
    model = RandomForestRegressor(
        n_estimators=200,
        random_state=0,
        n_jobs=-1
    )
    model.fit(X, y)
    return model

def _fit_xgboost(X, y):
    model = xgb.XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        objective="reg:squarederror"
    )
    model.fit(X, y)
    return model

# Train all models and select best
models = _train_all_models(X_train, y_train)
val_metrics = {name: _evaluate(m, X_val, y_val)
               for name, m in models.items()}
best_model = min(val_metrics, key=lambda k: val_metrics[k]["rmse"])
"""
    add_code_slide(prs, "7. Model Implementation (Python Code)", code)

    # =============================================
    # SLIDE 17: Model Evaluation
    # =============================================
    add_content_slide(prs, "8. Model Evaluation", [
        "Evaluation Metrics:",
        "• RMSE (Root Mean Squared Error)",
        "• MAE (Mean Absolute Error)",
        "• R² (Coefficient of Determination)",
        "",
        "Results on Validation Set:",
        "┌──────────────┬────────┬────────┬────────┐",
        "│ Model        │ RMSE   │ MAE    │ R²     │",
        "├──────────────┼────────┼────────┼────────┤",
        "│ Random Forest│ 3.90   │ 3.21   │ 0.31   │",
        "│ XGBoost      │ 3.63   │ 3.01   │ 0.40   │",
        "│ SVR          │ 5.01   │ 4.31   │ -0.14  │",
        "└──────────────┴────────┴────────┴────────┘",
        "",
        "Best Model: XGBoost (lowest RMSE)"
    ])

    # =============================================
    # SLIDE 18: Module 2 - Risk Mapping
    # =============================================
    add_content_slide(prs, "Module 2: Risk Mapping", [
        "AHP-Weighted Risk Indicators:",
        "",
        "┌────────────────────────┬────────┐",
        "│ Indicator              │ Weight │",
        "├────────────────────────┼────────┤",
        "│ Predicted Decline Rate │ 0.503  │",
        "│ Current Depth          │ 0.260  │",
        "│ Variability            │ 0.134  │",
        "│ Rainfall Dependence    │ 0.068  │",
        "│ LULC Change            │ 0.035  │",
        "└────────────────────────┴────────┘",
        "",
        "Consistency Ratio: 0.054 (< 0.10 threshold)",
        "Classification: Jenks Natural Breaks → 4 risk classes"
    ])

    # =============================================
    # SLIDE 19: Working Demo
    # =============================================
    add_content_slide(prs, "9. Working Demonstration", [
        "Demo Components:",
        "",
        "1. Run Full Pipeline:",
        "   $ cd Week4_Task4_Core_Implementation",
        "   $ python -m src.main",
        "",
        "2. Run Test Suite (13 tests):",
        "   $ python -m tests.test_modules",
        "",
        "3. Launch Dashboard:",
        "   $ streamlit run dashboard.py",
        "",
        "Outputs Generated:",
        "• module1_test_predictions.csv (160 predictions)",
        "• module2_risk_mapping.csv (100 locations)",
        "• 10 EDA visualization plots"
    ])

    # =============================================
    # SLIDE 20: Sample Output
    # =============================================
    output_code = """$ python -m src.main

[INFO] ============================================================
[INFO] GROUNDWATER DEPLETION PREDICTION AND RISK MAPPING
[INFO] ============================================================
[INFO] --- MODULE 1: Groundwater Level Prediction ---
[INFO] Data split - train: 512, val: 128, test: 160
[INFO] Training Random Forest ...
[INFO] Training XGBoost ...
[INFO] Training SVR ...
[INFO] xgboost - RMSE: 3.6261, MAE: 3.0093, R2: 0.4030
[INFO] Best model on validation: xgboost
[INFO] Module 1 completed.

[INFO] --- MODULE 2: Depletion Risk Mapping ---
[INFO] AHP weights computed
[INFO] Consistency Ratio: 0.0542 (< 0.10)
[INFO] Risk class distribution:
   Moderate: 42, High: 28, Low: 20, Very High: 10
[INFO] ALL MODULES COMPLETED SUCCESSFULLY
"""
    add_code_slide(prs, "Sample Pipeline Output", output_code)

    # =============================================
    # SLIDE 21: Dashboard Screenshot
    # =============================================
    add_content_slide(prs, "Interactive Dashboard", [
        "Built with Streamlit + Plotly",
        "",
        "Features:",
        "• Overview: Key metrics at a glance",
        "• Module 1: Model comparison charts",
        "• Module 2: Risk distribution visualizations",
        "• Data tables with filtering",
        "",
        "To Run:",
        "$ pip install streamlit plotly",
        "$ streamlit run dashboard.py",
        "",
        "Opens in browser at http://localhost:8501"
    ])

    # =============================================
    # SLIDE 22: Conclusion
    # =============================================
    add_content_slide(prs, "Conclusion", [
        "Achievements:",
        "✓ Collected 123,391 real CGWB groundwater records",
        "✓ Comprehensive EDA with 10 visualizations",
        "✓ Implemented 3 ML models (RF, XGBoost, SVR)",
        "✓ XGBoost selected as best (RMSE: 3.63)",
        "✓ AHP risk mapping with Jenks classification",
        "✓ 13 test cases, all passing",
        "✓ Interactive Streamlit dashboard",
        "",
        "Next Steps:",
        "• Integrate real-time data updates",
        "• Implement spatial interpolation (Kriging)",
        "• Deploy dashboard for stakeholders"
    ])

    # =============================================
    # SLIDE 23: Thank You
    # =============================================
    add_title_slide(prs, "Thank You!", "Questions?")

    # Save
    output_path = OUTPUT_DIR / 'Groundwater_Depletion_Presentation.pptx'
    prs.save(output_path)
    print(f"Presentation saved to: {output_path}")
    return output_path

if __name__ == '__main__':
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    create_presentation()
