"""
data_processor.py
Process real Karnataka CGWB groundwater data for ML pipeline

Loads the cleaned dataset and creates feature tables for:
- Module 1: Time-series prediction
- Module 2: Risk indicator computation
"""

from __future__ import annotations
import logging
import math
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

from .config import GWL_MAX_M, GWL_MIN_M, MIN_RECORDS_PER_STATION

DATA_DIR = Path(__file__).parent.parent / 'data' / 'raw'

# ---------------------------------------------------------------------------
# District name canonicalisation
# ---------------------------------------------------------------------------
# Karnataka renamed several districts (Mysore -> Mysuru, Gulbarga -> Kalaburagi,
# ...) and the CGWB extraction sheet truncates some names to 13 characters.
# The CGWB level export contains BOTH the old and new spellings, so without
# this map a single district is split into two rows AND fails to join to its
# assessment category.
DISTRICT_ALIASES = {
    "BAGALKOT": "BAGALKOTE",
    "BANGALORE RURAL": "BENGALURU RURAL", "BANGALORE RUR": "BENGALURU RURAL",
    "BANGALORE URBAN": "BENGALURU URBAN", "BANGALORE URB": "BENGALURU URBAN",
    "BELGAUM": "BELAGAVI",
    "BIJAPUR": "VIJAYAPURA",
    "CHAMARAJANAGAR": "CHAMARAJANAGARA", "CHAMRAJNAGARA": "CHAMARAJANAGARA",
    "CHIKMAGALUR": "CHIKKAMAGALURU", "CHIKKAMAGALUR": "CHIKKAMAGALURU",
    "CHIKBALLAPUR": "CHIKKABALLAPURA", "CHIKKABALLAPUR": "CHIKKABALLAPURA",
    "DAKSHIN KANNADA": "DAKSHINA KANNADA", "DAKSHIN KANNA": "DAKSHINA KANNADA",
    "DAVANGERE": "DAVANAGERE",
    "GULBARGA": "KALABURAGI", "KALBURAGI": "KALABURAGI",
    "MYSORE": "MYSURU",
    "SHIMOGA": "SHIVAMOGGA",
    "TUMKUR": "TUMAKURU",
    "UTTAR KANNADA": "UTTARA KANNADA",
    "RAMANAGARAM": "RAMANAGARA",
}



# Taluk-level canonicalisation.  CGWB assesses groundwater per *taluk*, so the
# risk map is built at that unit; this maps the level export's Tehsil spellings
# onto the extraction sheet's Taluk names.
TALUK_ALIASES = {
    "BAGALKOT": "BAGALKOTE", "BELGAUM": "BELAGAVI", "BELLARY": "BALLARI",
    "BIJAPUR": "VIJAYAPURA", "CHAMARAJANAGAR": "CHAMRAJNAGARA",
    "CHAMARAJANAGARA": "CHAMRAJNAGARA", "CHIKMAGALUR": "CHIKKAMAGALURU",
    "CHIKAMAGALUR": "CHIKKAMAGALURU", "GULBARGA": "KALABURAGI",
    "KALBURAGI": "KALABURAGI", "MYSORE": "MYSURU", "SHIMOGA": "SHIVAMOGGA",
    "TUMKUR": "TUMAKURU", "HOSPET": "HOSAPETE", "SIRSI": "SIRSI",
    "CHANNAPATNA": "CHANNAPATANA", "SEDAM": "SEDAM",
    "CHIKNAYAKANHALLI": "CHICKNAYAKANHALLI",
    "CHIKKANAYAKANAHALLI": "CHICKNAYAKANHALLI",
    "KRISHNARAJPET": "K R PET", "KRISHNARAJAPET": "K R PET",
    "CHANNARAYAPATNA": "C R PATNA", "BRAHMAVAR": "BRAMHAVARA",
    "BYNDOOR": "BYNDURU", "DANDELI": "DANDELLI", "ANEKAL": "ANEKAL",
    "BANGARAPET": "BANGARPET", "ATHNI": "ATHANI", "BAILHONGAL": "BAILAHONGAL",
    "BELTANGADI": "BELTHANGADI", "CHITAPUR": "CHITHAPUR",
    "ANNIGERI": "ANNIGERI", "ALNAVAR": "ALNAVARA",
    # verified spelling variants between the level export and the CGWB sheet
    "BANGALORE NORTH": "BENGALURU NORTH", "BANGALORE SOUTH": "BENGALURU SOUTH",
    "BANGALORE EAST": "BENGALURU EAST", "DAVANAGERE": "DAVANGERE",
    "DEVANHALLI": "DEVENHALLI", "DODBALLAPUR": "DODABALLAPUR",
    "GAURIBIDANUR": "GAURIBIDALUR", "HONNALI": "HONNALLI",
    "HOSDURGA": "HOSADURGA", "HUKERI": "HUKKERI", "KAMALAPUR": "KAMALAPURA",
    "KARWAR": "KARVAR", "KRISHNARAJANAGARA": "KRISHNRAJANAGARA",
    "KUNDGOL": "KUNDAGOL", "MALVALLI": "MALAVALLI", "MANGALORE": "MANGALURU",
    "MUNDGOD": "MUNDOG", "PIRIYAPATNA": "PRIYAPATNA",
    "RAMANAGARAM": "RANMANAGARA", "SAVANUR": "SAVANNUR",
    "SHAHABAD": "SHAHBADHA", "SHAHAPUR": "SHAHPUR", "SHIKARPUR": "SHIKARIPUR",
    "SIDLAGHATTA": "SIDLAGHATA",
    "TIRUMAKUDAL-NARSIPUR": "TIRUMAKUDAL NARSIPURA",
    # historical taluk names, checked against the district they sit in
    "PARASGAD": "SAUNDATTI",        # Belagavi - NOT Pavagada, which fuzzy matching suggested
    "SAMPGAON": "BAILAHONGAL",      # Belagavi
    "MANJARABAD": "SAKLESHPUR",     # Hassan
    "DEVADURGA": "DEODRUG",         # Raichur
    "NARASIMHARAJAPURA": "N R PURA",  # Chikkamagaluru
}


def canonical_taluk(name) -> str:
    """Map any spelling of a taluk/tehsil to one canonical upper-case name."""
    if pd.isna(name):
        return ""
    key = " ".join(str(name).strip().upper().replace(".", "").split())
    return TALUK_ALIASES.get(key, key)


def canonical_district(name) -> str:
    """Map any spelling of a Karnataka district to one canonical name."""
    if pd.isna(name):
        return ""
    key = str(name).strip().upper().replace(".", "")
    key = " ".join(key.split())
    return DISTRICT_ALIASES.get(key, key)




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
            df = df[(df['GWL_m'] >= GWL_MIN_M) & (df['GWL_m'] <= GWL_MAX_M)]
            df = df.dropna(subset=['GWL_m', 'Date', 'District'])

            df.to_csv(clean_path, index=False)
            logger.info(f"Saved cleaned data: {len(df)} records")
            return df
        else:
            raise FileNotFoundError(f"Data files not found in {DATA_DIR}")

    logger.info(f"Loading cleaned data from {clean_path}")
    df = pd.read_csv(clean_path, parse_dates=['Date'])
    n_before = df['District'].nunique()
    df['District'] = df['District'].map(canonical_district)
    logger.info("District names canonicalised: %d -> %d unique districts",
                n_before, df['District'].nunique())
    return df


def load_extraction_data() -> pd.DataFrame:
    """Load the taluk-wise extraction data."""
    path = DATA_DIR / 'karnataka_gw_extraction_2020.csv'
    if not path.exists():
        raise FileNotFoundError(f"Extraction data not found: {path}")

    df = pd.read_csv(path)
    logger.info(f"Loaded extraction data: {len(df)} taluks")
    return df


def create_station_features(df: pd.DataFrame, min_records: int = MIN_RECORDS_PER_STATION,
                            with_rainfall: bool = True) -> pd.DataFrame:
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

    # Attach real rainfall (NASA POWER) when it has been downloaded
    if with_rainfall:
        try:
            from .rainfall import DAILY_CSV, attach_to_observations, quarterly_features
            if DAILY_CSV.exists():
                daily = pd.read_csv(DAILY_CSV, parse_dates=['date'])
                monthly = quarterly_features(daily)
                df = attach_to_observations(df, monthly)
            else:
                logger.warning("No rainfall cache found - run `python -m src.rainfall` "
                               "to add rainfall features")
        except Exception as exc:                      # never block the pipeline
            logger.warning("Rainfall features unavailable (%s)", exc)

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



# ---------------------------------------------------------------------------
# Trend estimation: Mann-Kendall test + Sen's slope
# ---------------------------------------------------------------------------

def mann_kendall_sens_slope(times: np.ndarray, values: np.ndarray):
    """Return (sen_slope_per_year, p_value, trend_label).

    Non-parametric trend estimation as specified in the Week 3 design.  Sen's
    slope is the median of all pairwise slopes, so it is robust to the outliers
    and irregular sampling typical of well records.  Significance comes from
    the Mann-Kendall S statistic under the normal approximation with a tie
    correction.  Positive slope = water table deepening = depletion.
    """
    t = np.asarray(times, dtype=float)
    x = np.asarray(values, dtype=float)
    ok = ~np.isnan(t) & ~np.isnan(x)
    t, x = t[ok], x[ok]
    n = len(x)
    if n < 10:
        return np.nan, np.nan, "insufficient data"

    # Sen's slope - median of pairwise slopes
    idx_i, idx_j = np.triu_indices(n, k=1)
    dt = t[idx_j] - t[idx_i]
    valid = dt != 0
    slopes = (x[idx_j][valid] - x[idx_i][valid]) / dt[valid]
    sen = float(np.median(slopes)) if slopes.size else np.nan

    # Mann-Kendall S statistic
    s = float(np.sum(np.sign(x[idx_j] - x[idx_i])))
    _, counts = np.unique(x, return_counts=True)
    tie_term = np.sum(counts * (counts - 1) * (2 * counts + 5))
    var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0
    if var_s <= 0:
        return sen, np.nan, "no trend"
    z = (s - np.sign(s)) / np.sqrt(var_s) if s != 0 else 0.0
    # two-sided p-value from the standard normal survival function
    p = float(math.erfc(abs(z) / math.sqrt(2)))

    if p >= 0.05:
        label = "no significant trend"
    elif sen > 0:
        label = "significant decline"      # depth increasing
    else:
        label = "significant recovery"
    return sen, p, label


def station_trends(gwl_df: pd.DataFrame,
                   min_records: int = MIN_RECORDS_PER_STATION) -> pd.DataFrame:
    """Per-station Mann-Kendall / Sen's slope trend (metres per year)."""
    df = gwl_df.dropna(subset=['GWL_m', 'Date']).copy()
    df['t_years'] = pd.to_datetime(df['Date']).map(
        lambda d: d.year + (d.day_of_year - 1) / 365.25)

    rows = []
    for (station, district), g in df.groupby(['Station', 'District']):
        if len(g) < min_records:
            continue
        sen, p, label = mann_kendall_sens_slope(g['t_years'].values, g['GWL_m'].values)
        if np.isnan(sen):
            continue
        rows.append({'Station': station, 'District': district,
                     'sens_slope_m_per_yr': sen, 'mk_p_value': p, 'mk_trend': label})

    out = pd.DataFrame(rows)
    logger.info("Mann-Kendall/Sen trends computed for %d stations", len(out))
    if len(out):
        sig = (out['mk_p_value'] < 0.05)
        n_dec = int((sig & (out['sens_slope_m_per_yr'] > 0)).sum())
        n_rec = int((sig & (out['sens_slope_m_per_yr'] < 0)).sum())
        # the remainder (p >= 0.05, or a Sen's slope of exactly zero) so the
        # three counts always sum to the number of stations tested
        logger.info("  significant declining: %d | significant recovery: %d | no trend: %d | total: %d",
                    n_dec, n_rec, len(out) - n_dec - n_rec, len(out))
    return out


def _norm_district(name) -> str:
    """Normalise a district name so the GWL and extraction tables can be joined.

    The CGWB extraction CSV stores districts in upper case ("BAGALKOT") while
    the groundwater-level export uses title case ("Bagalkot").  Joining on the
    raw strings silently produced an all-NaN category column, which disabled
    the CGWB validation in Module 2.
    """
    return canonical_district(name)


def compute_seasonal_recovery(gwl_df: pd.DataFrame) -> pd.Series:
    """Mean pre-monsoon minus post-monsoon depth, per district (metres).

    CGWB measures in January, May (pre-monsoon), August and November
    (post-monsoon).  Depth is measured downwards, so a positive value means the
    water table rises after the monsoon.  A large recovery means the district
    leans heavily on monsoon recharge, which is used as a measurable proxy for
    monsoon dependence.
    """
    pre = gwl_df[gwl_df['Month'].isin([4, 5, 6])].groupby('District')['GWL_m'].mean()
    post = gwl_df[gwl_df['Month'].isin([10, 11, 12])].groupby('District')['GWL_m'].mean()
    return (pre - post).rename('seasonal_recovery')


def create_district_indicators(
    gwl_df: pd.DataFrame,
    extraction_df: pd.DataFrame,
    forecast_trends: pd.Series | None = None,
) -> pd.DataFrame:
    """Build the district-level risk indicators consumed by Module 2.

    Indicators (all measured, none synthesised):

    * ``predicted_decline_rate`` - m/year, from Module 1 forecasts when
      ``predicted_trends`` is supplied; otherwise the observed historical trend
      is used and the caller is warned.
    * ``current_depth``          - most recent annual mean depth to water (m).
    * ``variability``            - coefficient of variation of the GWL series.
    * ``seasonal_recovery``      - pre-monsoon minus post-monsoon depth (m).

    ``cgwb_category`` and ``extraction_stage`` are attached for validation only
    and are never used to build the risk index.
    """
    logger.info("Creating district risk indicators...")

    if 'Month' not in gwl_df.columns:
        gwl_df = gwl_df.copy()
        gwl_df['Month'] = pd.to_datetime(gwl_df['Date']).dt.month
    if 'Year' not in gwl_df.columns:
        gwl_df['Year'] = pd.to_datetime(gwl_df['Date']).dt.year

    stats = gwl_df.groupby('District').agg(
        mean_gwl=('GWL_m', 'mean'),
        std_gwl=('GWL_m', 'std'),
        records=('GWL_m', 'count'),
        lat=('Latitude', 'mean'),
        lon=('Longitude', 'mean'),
    ).reset_index()

    # Current depth: mean over the most recent three years of record.
    last_year = int(gwl_df['Year'].max())
    recent = gwl_df[gwl_df['Year'] >= last_year - 2]
    stats['current_depth'] = stats['District'].map(
        recent.groupby('District')['GWL_m'].mean()
    )
    stats['current_depth'] = stats['current_depth'].fillna(stats['mean_gwl'])

    # Variability (coefficient of variation).
    stats['variability'] = stats['std_gwl'] / stats['mean_gwl']

    # Seasonal recovery.
    stats['seasonal_recovery'] = stats['District'].map(compute_seasonal_recovery(gwl_df))

    # ------------------------------------------------------------------
    # Trend indicator: Mann-Kendall / Sen's slope per station, averaged by
    # district (metres per year, positive = deepening).
    #
    # The Week 4 implementation used the slope of Module 1's recursive
    # four-quarter forecast instead.  That was wrong: the recursive forecast
    # reverts to the training mean (76% of stations moved toward the overall
    # mean; corr(last observed depth, "trend") = -0.67), so it measured how far
    # the last reading sat from average, not depletion.  Module 1's validated
    # one-step forecast is kept as a cross-check column only.
    # ------------------------------------------------------------------
    st = station_trends(gwl_df)
    if len(st):
        by_district = st.groupby('District')
        stats['decline_rate'] = stats['District'].map(by_district['sens_slope_m_per_yr'].mean())
        stats['n_stations_trended'] = stats['District'].map(by_district.size())
        sig_decline = st[(st['mk_p_value'] < 0.05) & (st['sens_slope_m_per_yr'] > 0)]
        stats['pct_stations_declining'] = (
            stats['District'].map(sig_decline.groupby('District').size())
            .fillna(0) / stats['n_stations_trended'] * 100
        )
    else:
        stats['decline_rate'] = np.nan

    if forecast_trends is not None:
        stats['forecast_trend_m_per_yr'] = stats['District'].map(forecast_trends)

    # Attach CGWB assessment (validation only) with a normalised join key.
    ext = extraction_df.copy()
    ext['_key'] = ext['Name of District'].map(_norm_district)
    ext_agg = ext.groupby('_key').agg(
        extraction_stage=('Stage of GW extraction (%)', 'mean'),
        cgwb_category=('Categorization',
                       lambda x: x.astype(str).str.strip().str.lower().mode().iloc[0]
                       if len(x.mode()) else None),
    ).reset_index()

    stats['_key'] = stats['District'].map(_norm_district)
    indicators = stats.merge(ext_agg, on='_key', how='left').drop(columns='_key')

    unmatched = indicators['cgwb_category'].isna().sum()
    if unmatched:
        logger.warning("%d districts could not be matched to CGWB categories", unmatched)

    indicators = indicators.dropna(
        subset=['decline_rate', 'current_depth', 'variability', 'seasonal_recovery']
    )

    logger.info("District indicators created: %d districts", len(indicators))
    return indicators



def create_taluk_indicators(gwl_df: pd.DataFrame, extraction_df: pd.DataFrame,
                            rainfall_dep: pd.Series | None = None,
                            min_stations: int = 2) -> pd.DataFrame:
    """Risk indicators at TALUK level - the unit CGWB actually assesses.

    Working at taluk level rather than district level means the validation is
    one-to-one against CGWB's own assessment unit (227 taluks) instead of
    comparing against a district-level mode of those categories, and it gives
    planners roughly six times the spatial resolution.
    """
    logger.info("Creating taluk risk indicators ...")

    df = gwl_df.copy()
    df['Taluk'] = df['Tehsil'].map(canonical_taluk)
    df = df[df['Taluk'].str.len() > 1]
    if 'Month' not in df.columns:
        df['Month'] = pd.to_datetime(df['Date']).dt.month
    if 'Year' not in df.columns:
        df['Year'] = pd.to_datetime(df['Date']).dt.year

    stats = df.groupby('Taluk').agg(
        District=('District', lambda x: x.mode().iloc[0] if len(x.mode()) else None),
        mean_gwl=('GWL_m', 'mean'), std_gwl=('GWL_m', 'std'),
        records=('GWL_m', 'count'), n_stations=('Station', 'nunique'),
        lat=('Latitude', 'mean'), lon=('Longitude', 'mean'),
    ).reset_index()
    stats = stats[stats['n_stations'] >= min_stations]

    last_year = int(df['Year'].max())
    recent = df[df['Year'] >= last_year - 2]
    stats['current_depth'] = stats['Taluk'].map(
        recent.groupby('Taluk')['GWL_m'].mean()).fillna(stats['mean_gwl'])
    stats['variability'] = stats['std_gwl'] / stats['mean_gwl']

    pre = df[df['Month'].isin([4, 5, 6])].groupby('Taluk')['GWL_m'].mean()
    post = df[df['Month'].isin([10, 11, 12])].groupby('Taluk')['GWL_m'].mean()
    stats['seasonal_recovery'] = stats['Taluk'].map(pre - post)

    # Mann-Kendall / Sen's slope per station, averaged over the taluk
    st = station_trends(df)
    if len(st):
        st['Taluk'] = st['Station'].map(
            df.drop_duplicates('Station').set_index('Station')['Taluk'])
        by = st.dropna(subset=['Taluk']).groupby('Taluk')
        stats['decline_rate'] = stats['Taluk'].map(by['sens_slope_m_per_yr'].mean())
        stats['n_stations_trended'] = stats['Taluk'].map(by.size())
        sig = st[(st['mk_p_value'] < 0.05) & (st['sens_slope_m_per_yr'] > 0)]
        stats['pct_stations_declining'] = (
            stats['Taluk'].map(sig.groupby('Taluk').size()).fillna(0)
            / stats['n_stations_trended'] * 100)

    if rainfall_dep is not None:
        stats['rainfall_dependence'] = stats['Taluk'].map(rainfall_dep)
        missing = int(stats['rainfall_dependence'].isna().sum())
        if missing:
            logger.warning("%d taluks have no rainfall-dependence value; "
                           "filled with the state median", missing)
            stats['rainfall_dependence'] = stats['rainfall_dependence'].fillna(
                stats['rainfall_dependence'].median())

    # CGWB assessment for validation only - one row per taluk, exact join
    ext = extraction_df.copy()
    ext['Taluk_key'] = ext['Taluk'].map(canonical_taluk)
    ext_agg = ext.groupby('Taluk_key').agg(
        extraction_stage=('Stage of GW extraction (%)', 'mean'),
        cgwb_category=('Categorization',
                       lambda x: x.astype(str).str.strip().str.lower().mode().iloc[0]
                       if len(x.mode()) else None)).reset_index()
    out = stats.merge(ext_agg, left_on='Taluk', right_on='Taluk_key',
                      how='left').drop(columns='Taluk_key')

    matched = int(out['cgwb_category'].notna().sum())
    logger.info("Taluk indicators: %d taluks, %d matched to a CGWB category (%.0f%%)",
                len(out), matched, 100 * matched / max(len(out), 1))

    needed = ['decline_rate', 'current_depth', 'variability', 'seasonal_recovery']
    out = out.dropna(subset=[c for c in needed if c in out.columns])
    logger.info("Taluk indicators complete: %d taluks", len(out))
    return out


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
