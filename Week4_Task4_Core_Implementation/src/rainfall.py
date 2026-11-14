"""
rainfall.py - real daily rainfall for every Karnataka taluk, 1996-2024.

Groundwater cannot be modelled honestly without rainfall: it is the main
recharge driver, and the Week 2/3 design called for it. IMD's gridded product
needs a registered/paid download, so this module uses **NASA POWER**
(PRECTOTCORR, bias-corrected MERRA-2 precipitation) which is free, needs no
key, and serves a whole bounding box in one request.

    python -m src.rainfall          # downloads once, caches to data/raw/

Why NASA POWER and not ERA5/Open-Meteo: Open-Meteo's free tier is rate-limited
on (locations x days), and 180 taluks x 29 years triggered multi-minute
cooldowns. POWER's regional endpoint returns the 105 grid cells covering
Karnataka for a whole year in about two seconds. Cross-check at Kolar for
2020: POWER 1139 mm vs ERA5 1104 mm, a 3% difference.

Grid: 0.5 deg latitude x 0.625 deg longitude (~55 km). Each taluk is assigned
the nearest grid cell to its station centroid.

What it produces
----------------
`data/raw/rainfall_taluk_daily.csv`     one row per taluk-day (mm)
`data/raw/rainfall_taluk_monthly.csv`   features joined to CGWB quarters:

    rain_q           rainfall in the 3 months to the observation (mm)
    rain_prev_q      the 3 months before that (mm)
    rain_12m         rolling 12-month rainfall (mm)
    rain_monsoon     June-September total for that water year (mm)
    rain_anomaly_12m rain_12m minus the taluk's long-term 12-month mean (mm)

Source: NASA Langley Research Center POWER Project (https://power.larc.nasa.gov),
PRECTOTCORR daily corrected total precipitation.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

DATA = Path(__file__).parent.parent / "data" / "raw"
DAILY_CSV = DATA / "rainfall_taluk_daily.csv"
QUARTERLY_CSV = DATA / "rainfall_taluk_monthly.csv"

POWER = "https://power.larc.nasa.gov/api/temporal/daily/regional"
BBOX = dict(lat_min=11.5, lat_max=18.6, lon_min=74.0, lon_max=78.7)
START_YEAR, END_YEAR = 1996, 2024
PAUSE = 0.5
MONTHLY_CSV = DATA / "rainfall_taluk_monthly.csv"


def taluk_centroids(gwl: pd.DataFrame) -> pd.DataFrame:
    """Mean station position per taluk - rainfall is sampled at the nearest cell."""
    from .data_processor import canonical_taluk

    df = gwl.copy()
    df["Taluk"] = df["Tehsil"].map(canonical_taluk)
    cen = (df[df["Taluk"].str.len() > 1]
           .groupby("Taluk")
           .agg(lat=("Latitude", "mean"), lon=("Longitude", "mean"),
                stations=("Station", "nunique"))
           .reset_index())
    cen = cen[cen["lat"].between(11, 19) & cen["lon"].between(74, 79)]
    logger.info("%d taluk centroids to match against the rainfall grid", len(cen))
    return cen


def _fetch_year(year: int, retries: int = 3) -> pd.DataFrame:
    """One year of daily rainfall for every grid cell over Karnataka."""
    q = urllib.parse.urlencode({
        "parameters": "PRECTOTCORR", "community": "AG",
        "latitude-min": BBOX["lat_min"], "latitude-max": BBOX["lat_max"],
        "longitude-min": BBOX["lon_min"], "longitude-max": BBOX["lon_max"],
        "start": f"{year}0101", "end": f"{year}1231", "format": "JSON",
    })
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(f"{POWER}?{q}", timeout=300) as r:
                payload = json.load(r)
            rows = []
            for feat in payload.get("features", []):
                lon, lat = feat["geometry"]["coordinates"][:2]
                for day, mm in feat["properties"]["parameter"]["PRECTOTCORR"].items():
                    if mm is not None and mm > -900:          # -999 = fill value
                        rows.append((lat, lon, day, mm))
            return pd.DataFrame(rows, columns=["cell_lat", "cell_lon", "day", "rain_mm"])
        except Exception as exc:
            if attempt == retries:
                raise
            logger.warning("year %d failed (%s); retrying", year, exc)
            time.sleep(5 * attempt)
    return pd.DataFrame()


def download_daily(gwl: pd.DataFrame, force: bool = False) -> pd.DataFrame:
    """Download (once) and cache daily rainfall per taluk."""
    if DAILY_CSV.exists() and not force:
        logger.info("Using cached rainfall: %s", DAILY_CSV.name)
        return pd.read_csv(DAILY_CSV, parse_dates=["date"])

    frames = []
    for year in range(START_YEAR, END_YEAR + 1):
        logger.info("NASA POWER: %d", year)
        frames.append(_fetch_year(year))
        time.sleep(PAUSE)
    grid = pd.concat(frames, ignore_index=True)
    grid["date"] = pd.to_datetime(grid["day"], format="%Y%m%d")
    logger.info("Grid downloaded: %d cells x %d days",
                grid[["cell_lat", "cell_lon"]].drop_duplicates().shape[0],
                grid["date"].nunique())

    # assign each taluk the nearest grid cell
    cen = taluk_centroids(gwl)
    cells = grid[["cell_lat", "cell_lon"]].drop_duplicates().to_numpy()
    assign = {}
    for _, row in cen.iterrows():
        d2 = (cells[:, 0] - row["lat"]) ** 2 + (cells[:, 1] - row["lon"]) ** 2
        assign[row["Taluk"]] = tuple(cells[int(np.argmin(d2))])

    lookup = pd.DataFrame(
        [(t, c[0], c[1]) for t, c in assign.items()],
        columns=["Taluk", "cell_lat", "cell_lon"])
    out = (lookup.merge(grid, on=["cell_lat", "cell_lon"], how="left")
                 [["Taluk", "date", "rain_mm"]])
    out["rain_mm"] = pd.to_numeric(out["rain_mm"], errors="coerce").fillna(0.0)

    DATA.mkdir(parents=True, exist_ok=True)
    out.to_csv(DAILY_CSV, index=False)
    logger.info("Saved %s (%d rows, %d taluks, %s to %s)", DAILY_CSV.name, len(out),
                out["Taluk"].nunique(), out["date"].min().date(), out["date"].max().date())
    return out


def quarterly_features(daily: pd.DataFrame) -> pd.DataFrame:
    """Turn daily rainfall into the features Module 1 and Module 2 consume."""
    d = daily.sort_values(["Taluk", "date"]).copy()
    d = d.set_index("date")

    rows = []
    for taluk, g in d.groupby("Taluk"):
        s = g["rain_mm"].astype(float)
        monthly = s.resample("MS").sum()
        feat = pd.DataFrame({"rain_1m": monthly})
        feat["rain_q"] = monthly.rolling(3, min_periods=1).sum()
        feat["rain_prev_q"] = feat["rain_q"].shift(3)
        feat["rain_12m"] = monthly.rolling(12, min_periods=6).sum()
        # Total of the LAST COMPLETED June-September monsoon.
        # Using the current season would leak: an August observation would
        # otherwise carry September's rainfall, which has not happened yet.
        # The season is treated as complete from October onwards.
        jjas = s[s.index.month.isin([6, 7, 8, 9])].resample("YE").sum()
        jjas.index = jjas.index.year
        feat["rain_monsoon"] = [jjas.get(ts.year if ts.month >= 10 else ts.year - 1, np.nan)
                                for ts in feat.index]
        feat["rain_anomaly_12m"] = feat["rain_12m"] - feat["rain_12m"].mean()
        feat["Taluk"] = taluk
        rows.append(feat.reset_index().rename(columns={"index": "month"}))

    out = pd.concat(rows, ignore_index=True)
    out = out.rename(columns={out.columns[0]: "month"})
    out.to_csv(QUARTERLY_CSV, index=False)
    logger.info("Saved %s (%d taluk-months)", QUARTERLY_CSV.name, len(out))
    return out


def attach_to_observations(gwl: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    """Join the rainfall features onto each groundwater observation."""
    from .data_processor import canonical_taluk

    g = gwl.copy()
    g["Taluk"] = g["Tehsil"].map(canonical_taluk)
    g["month"] = pd.to_datetime(g["Date"]).values.astype("datetime64[M]")
    m = monthly.copy()
    m["month"] = pd.to_datetime(m["month"]).values.astype("datetime64[M]")

    merged = g.merge(
        m[["Taluk", "month", "rain_q", "rain_prev_q", "rain_12m",
           "rain_monsoon", "rain_anomaly_12m"]],
        on=["Taluk", "month"], how="left")
    cov = merged["rain_q"].notna().mean() * 100
    logger.info("Rainfall attached to %.1f%% of groundwater observations", cov)
    return merged


def rainfall_dependence(merged: pd.DataFrame) -> pd.Series:
    """Correlation between monsoon rainfall and post-monsoon recovery, per taluk.

    Recovery = pre-monsoon depth (May) minus post-monsoon depth (November) in the
    same year: how far the water table rose over that monsoon. A taluk whose
    recovery tracks the rain closely is highly monsoon-dependent, and therefore
    exposed in a weak year.
    """
    d = merged.copy()
    d["Year"] = pd.to_datetime(d["Date"]).dt.year
    d["Month"] = pd.to_datetime(d["Date"]).dt.month

    pre = (d[d["Month"].isin([4, 5, 6])]
           .groupby(["Taluk", "Year"])["GWL_m"].mean().rename("pre"))
    post = (d[d["Month"].isin([10, 11, 12])]
            .groupby(["Taluk", "Year"])["GWL_m"].mean().rename("post"))
    rain = (d[d["Month"].isin([10, 11, 12])]
            .groupby(["Taluk", "Year"])["rain_monsoon"].mean().rename("rain"))

    j = pd.concat([pre, post, rain], axis=1).dropna()
    j["recovery"] = j["pre"] - j["post"]

    out = {}
    for taluk, g in j.groupby(level=0):
        if len(g) >= 5 and g["rain"].std() > 0 and g["recovery"].std() > 0:
            out[taluk] = float(np.corrcoef(g["rain"], g["recovery"])[0, 1])
    logger.info("Rainfall dependence computed for %d taluks", len(out))
    return pd.Series(out, name="rainfall_dependence")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    from .data_processor import load_gwl_data

    gwl = load_gwl_data()
    daily = download_daily(gwl)
    monthly = quarterly_features(daily)
    merged = attach_to_observations(gwl, monthly)
    print(merged[["Station", "Date", "GWL_m", "rain_q", "rain_monsoon"]].head())
    print("\nrainfall dependence (sample):")
    print(rainfall_dependence(merged).describe())
