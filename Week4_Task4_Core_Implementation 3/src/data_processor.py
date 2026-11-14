"""
data_processor.py
Process real Karnataka CGWB groundwater data for ML pipeline

Loads the cleaned dataset and creates feature tables for:
- Module 1: Time-series prediction
- Module 2: Risk indicator computation
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / 'data' / 'raw'


def load_gwl_data() -> pd.DataFrame:
    """Load the cleaned GWL dataset."""
    clean_path = DATA_DIR / 'gwl_karnataka_clean.csv'

    if not clean_path.exists():
        # Try to load and clean raw data
        recent = DATA_DIR / 'gwl_karnataka_2021_2025.csv'
        historical = DATA_DIR / 'gwl_karnataka_1991_2020.csv'

        if recent.exists() and historical.exists():
            logger.info("Loading raw data files...")
            df1 = pd.read_csv(recent)
            df2 = pd.read_csv(historical)
            df = pd.concat([df2, df1], ignore_index=True)

            # Basic cleaning
            df['Date'] = pd.to_datetime(df['Data Acquisition Time'], format='%d-%m-%Y %H:%M', errors='coerce')
            df = df.rename(columns={'Groundwater Level Quarterly Manual (meter)': 'GWL_m'})
            df['GWL_m'] = pd.to_numeric(df['GWL_m'], errors='coerce')
            df = df[(df['GWL_m'] >= 0) & (df['GWL_m'] <= 100)]
            df = df.dropna(subset=['GWL_m', 'Date', 'District'])

            df.to_csv(clean_path, index=False)
            logger.info(f"Saved cleaned data: {len(df)} records")
            return df
        else:
            raise FileNotFoundError(f"Data files not found in {DATA_DIR}")

    logger.info(f"Loading cleaned data from {clean_path}")
    return pd.read_csv(clean_path, parse_dates=['Date'])


def load_extraction_data() -> pd.DataFrame:
    """Load the taluk-wise extraction data."""
    path = DATA_DIR / 'karnataka_gw_extraction_2020.csv'
    if not path.exists():
        raise FileNotFoundError(f"Extraction data not found: {path}")

    df = pd.read_csv(path)
    logger.info(f"Loaded extraction data: {len(df)} taluks")
    return df


def create_station_features(df: pd.DataFrame, min_records: int = 20) -> pd.DataFrame:
    """
    Create feature table for station-level prediction.

    Features:
    - Lag features (previous 1-4 quarters GWL)
    - Rolling statistics (mean, std over past year)
    - Seasonal indicators
    - Location features
    """
    logger.info("Creating station features...")

    df = df.copy()
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Quarter'] = df['Date'].dt.quarter

    # Sort by station and date
    df = df.sort_values(['Station', 'Date'])

    # Filter stations with enough records
    station_counts = df.groupby('Station').size()
    valid_stations = station_counts[station_counts >= min_records].index
    df = df[df['Station'].isin(valid_stations)]
    logger.info(f"Stations with >= {min_records} records: {len(valid_stations)}")

    # Create lag features per station
    for lag in [1, 2, 3, 4]:
        df[f'GWL_lag{lag}'] = df.groupby('Station')['GWL_m'].shift(lag)

    # Rolling statistics (past 4 quarters = 1 year)
    df['GWL_rolling_mean'] = df.groupby('Station')['GWL_m'].transform(
        lambda x: x.rolling(window=4, min_periods=2).mean().shift(1)
    )
    df['GWL_rolling_std'] = df.groupby('Station')['GWL_m'].transform(
        lambda x: x.rolling(window=4, min_periods=2).std().shift(1)
    )

    # Seasonal encoding
    df['sin_month'] = np.sin(2 * np.pi * df['Month'] / 12)
    df['cos_month'] = np.cos(2 * np.pi * df['Month'] / 12)

    # Target: next quarter's GWL
    df['target_gwl'] = df.groupby('Station')['GWL_m'].shift(-1)

    # Drop rows with NaN in critical columns
    feature_cols = ['GWL_lag1', 'GWL_lag2', 'GWL_rolling_mean', 'target_gwl']
    df = df.dropna(subset=feature_cols)

    logger.info(f"Feature table created: {len(df)} records")
    return df


def prepare_ml_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare X (features) and y (target) for ML training.
    """
    feature_cols = [
        'GWL_lag1', 'GWL_lag2', 'GWL_lag3', 'GWL_lag4',
        'GWL_rolling_mean', 'GWL_rolling_std',
        'sin_month', 'cos_month',
        'Latitude', 'Longitude'
    ]

    # Select available features
    available = [c for c in feature_cols if c in df.columns]

    X = df[available].copy()
    y = df['target_gwl'].copy()

    # Fill any remaining NaN
    X = X.fillna(X.mean())

    logger.info(f"ML data prepared: {X.shape[0]} samples, {X.shape[1]} features")
    return X, y


def create_district_indicators(gwl_df: pd.DataFrame, extraction_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create district-level risk indicators for Module 2.

    Indicators:
    - predicted_decline_rate: Computed from GWL trends
    - current_depth: Latest mean GWL
    - variability: CV of GWL
    - extraction_stage: From CGWB data
    """
    logger.info("Creating district risk indicators...")

    # Compute GWL statistics by district
    gwl_stats = gwl_df.groupby('District').agg({
        'GWL_m': ['mean', 'std', 'min', 'max', 'count'],
        'Latitude': 'mean',
        'Longitude': 'mean'
    })
    gwl_stats.columns = ['mean_gwl', 'std_gwl', 'min_gwl', 'max_gwl', 'records', 'lat', 'lon']
    gwl_stats = gwl_stats.reset_index()

    # Compute trend (simple linear slope)
    def compute_trend(group):
        if len(group) < 10:
            return np.nan
        group = group.sort_values('Date')
        x = np.arange(len(group))
        y = group['GWL_m'].values
        mask = ~np.isnan(y)
        if mask.sum() < 5:
            return np.nan
        slope, _ = np.polyfit(x[mask], y[mask], 1)
        return slope  # m per observation (quarterly)

    trends = gwl_df.groupby('District').apply(compute_trend)
    gwl_stats['decline_rate'] = gwl_stats['District'].map(trends)

    # Variability (CV)
    gwl_stats['variability'] = gwl_stats['std_gwl'] / gwl_stats['mean_gwl']

    # Merge with extraction data
    extraction_agg = extraction_df.groupby('Name of District').agg({
        'Stage of GW extraction (%)': 'mean',
        'Categorization': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'unknown'
    }).reset_index()
    extraction_agg.columns = ['District', 'extraction_stage', 'cgwb_category']

    # Merge
    indicators = gwl_stats.merge(extraction_agg, on='District', how='left')

    # Rename for Module 2 compatibility
    indicators = indicators.rename(columns={
        'decline_rate': 'predicted_decline_rate',
        'mean_gwl': 'current_depth'
    })

    # Add placeholder for rainfall_dependence and lulc_change
    indicators['rainfall_dependence'] = np.random.uniform(0.3, 0.8, len(indicators))
    indicators['lulc_change'] = np.random.uniform(0.05, 0.25, len(indicators))

    indicators = indicators.dropna(subset=['predicted_decline_rate', 'current_depth'])

    logger.info(f"District indicators created: {len(indicators)} districts")
    return indicators


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

    # Test loading
    gwl = load_gwl_data()
    print(f"GWL records: {len(gwl)}")

    extraction = load_extraction_data()
    print(f"Extraction taluks: {len(extraction)}")

    # Create features
    features = create_station_features(gwl)
    print(f"Feature table: {len(features)} records")

    X, y = prepare_ml_data(features)
    print(f"ML data: {X.shape}")

    # Create indicators
    indicators = create_district_indicators(gwl, extraction)
    print(f"District indicators: {len(indicators)} districts")
