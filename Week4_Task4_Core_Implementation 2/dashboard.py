"""
Streamlit Dashboard for Groundwater Depletion Prediction and Risk Mapping

Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Karnataka Groundwater Risk Dashboard",
    page_icon="💧",
    layout="wide"
)

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models"

# Title
st.title("💧 Karnataka Groundwater Depletion Risk Dashboard")
st.markdown("**Spatio-Temporal Prediction and Risk Mapping System**")
st.markdown("---")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Module", ["Overview", "Module 1: Prediction", "Module 2: Risk Mapping"])

# Load data
@st.cache_data
def load_module1_data():
    pred_path = OUTPUT_DIR / "module1_test_predictions.csv"
    meta_path = MODEL_DIR / "module1_best_model.json"

    predictions = None
    metadata = None

    if pred_path.exists():
        predictions = pd.read_csv(pred_path)
    if meta_path.exists():
        with open(meta_path) as f:
            metadata = json.load(f)

    return predictions, metadata

@st.cache_data
def load_module2_data():
    risk_path = OUTPUT_DIR / "module2_risk_mapping.csv"
    if risk_path.exists():
        return pd.read_csv(risk_path)
    return None

# Overview Page
if page == "Overview":
    st.header("System Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Module 1: GWL Prediction")
        st.markdown("""
        - **Purpose**: Predict future groundwater levels
        - **Models**: Random Forest, XGBoost, SVR, LSTM
        - **Best Model**: XGBoost (auto-selected)
        - **Metrics**: RMSE, MAE, R²
        """)

    with col2:
        st.subheader("🗺️ Module 2: Risk Mapping")
        st.markdown("""
        - **Purpose**: Classify depletion risk zones
        - **Method**: AHP weighted indicators + Jenks breaks
        - **Classes**: Low, Moderate, High, Very High
        - **Validation**: Against CGWB categories
        """)

    st.markdown("---")
    st.subheader("📈 Quick Stats")

    predictions, metadata = load_module1_data()
    risk_data = load_module2_data()

    col1, col2, col3, col4 = st.columns(4)

    if metadata:
        col1.metric("Best Model", metadata.get("selected_model", "N/A").upper())
        col2.metric("Test RMSE", f"{metadata.get('test_rmse', 0):.2f}")

    if risk_data is not None:
        col3.metric("Locations Assessed", len(risk_data))
        high_risk = len(risk_data[risk_data["risk_class"] >= 3])
        col4.metric("High/Very High Risk", f"{high_risk} ({high_risk/len(risk_data)*100:.1f}%)")

# Module 1 Page
elif page == "Module 1: Prediction":
    st.header("Module 1: Groundwater Level Prediction")

    predictions, metadata = load_module1_data()

    if metadata:
        st.subheader("Model Performance")

        col1, col2, col3 = st.columns(3)
        col1.metric("Selected Model", metadata.get("selected_model", "N/A").upper())
        col2.metric("Test RMSE", f"{metadata.get('test_rmse', 0):.4f}")
        col3.metric("Test R²", f"{metadata.get('test_r2', 0):.4f}")

        # Model comparison chart
        st.subheader("Model Comparison (Validation Set)")
        model_data = pd.DataFrame({
            "Model": ["Random Forest", "XGBoost", "SVR"],
            "RMSE": [3.9006, 3.6261, 5.0142],
            "MAE": [3.2118, 3.0093, 4.3076],
            "R²": [0.3092, 0.4030, -0.1416]
        })

        fig = px.bar(model_data, x="Model", y="RMSE",
                    title="RMSE Comparison (Lower is Better)",
                    color="Model")
        st.plotly_chart(fig, use_container_width=True)

    if predictions is not None:
        st.subheader("Test Set Predictions")

        # Prediction time series
        fig = px.line(predictions, x="obs_idx", y="prediction",
                     title="Predicted Groundwater Depth Over Time",
                     labels={"obs_idx": "Observation Index", "prediction": "Predicted Depth (m)"})
        st.plotly_chart(fig, use_container_width=True)

        # Statistics
        st.subheader("Prediction Statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Min", f"{predictions['prediction'].min():.2f} m")
        col2.metric("Max", f"{predictions['prediction'].max():.2f} m")
        col3.metric("Mean", f"{predictions['prediction'].mean():.2f} m")
        col4.metric("Std Dev", f"{predictions['prediction'].std():.2f} m")
    else:
        st.warning("No prediction data found. Run the pipeline first.")

# Module 2 Page
elif page == "Module 2: Risk Mapping":
    st.header("Module 2: Depletion Risk Mapping")

    risk_data = load_module2_data()

    if risk_data is not None:
        # AHP Weights
        st.subheader("AHP Indicator Weights")
        weights_data = pd.DataFrame({
            "Indicator": ["Predicted Decline Rate", "Current Depth", "Variability",
                         "Rainfall Dependence", "LULC Change"],
            "Weight": [0.5028, 0.2602, 0.1344, 0.0678, 0.0348]
        })

        fig = px.pie(weights_data, values="Weight", names="Indicator",
                    title="Risk Indicator Weights (AHP)")
        st.plotly_chart(fig, use_container_width=True)

        # Risk Distribution
        st.subheader("Risk Class Distribution")

        col1, col2 = st.columns(2)

        with col1:
            risk_counts = risk_data["risk_label"].value_counts()
            fig = px.bar(x=risk_counts.index, y=risk_counts.values,
                        title="Number of Locations by Risk Class",
                        labels={"x": "Risk Class", "y": "Count"},
                        color=risk_counts.index,
                        color_discrete_map={
                            "Low": "green",
                            "Moderate": "yellow",
                            "High": "orange",
                            "Very High": "red"
                        })
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(risk_data, names="risk_label",
                        title="Risk Distribution (%)",
                        color="risk_label",
                        color_discrete_map={
                            "Low": "green",
                            "Moderate": "gold",
                            "High": "orange",
                            "Very High": "red"
                        })
            st.plotly_chart(fig, use_container_width=True)

        # Risk Index Distribution
        st.subheader("Risk Index Distribution")
        fig = px.histogram(risk_data, x="risk_index", nbins=20,
                          title="Distribution of Risk Index Values",
                          labels={"risk_index": "Risk Index (0-1)"},
                          color_discrete_sequence=["steelblue"])
        st.plotly_chart(fig, use_container_width=True)

        # Data Table
        st.subheader("Risk Assessment Data")
        display_cols = ["location_id", "risk_index", "risk_class", "risk_label"]
        if "cgwb_category" in risk_data.columns:
            display_cols.append("cgwb_category")

        st.dataframe(risk_data[display_cols].head(20), use_container_width=True)

        # Validation metrics
        st.subheader("Validation Against CGWB Categories")
        col1, col2 = st.columns(2)
        col1.metric("Accuracy", "68.0%")
        col2.metric("Cohen's Kappa", "0.536")
        st.info("Kappa > 0.5 indicates moderate agreement with CGWB assessment categories.")

    else:
        st.warning("No risk mapping data found. Run the pipeline first.")

# Footer
st.markdown("---")
st.markdown("*CAIML_Shobha_Rani_4_PS_160 | REVA University | 2026*")
