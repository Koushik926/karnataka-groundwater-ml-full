"""
Comprehensive EDA for Karnataka Groundwater Data
Generates all visualizations for the Saturday presentation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Setup
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

DATA_DIR = Path(__file__).parent.parent / 'data' / 'raw'
OUTPUT_DIR = Path(__file__).parent.parent / 'outputs' / 'eda_plots'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("KARNATAKA GROUNDWATER DATA - EXPLORATORY DATA ANALYSIS")
print("="*60)

# ============================================================
# 1. LOAD DATA
# ============================================================
print("\n1. LOADING DATASETS...")

# Groundwater levels 2021-2025
gwl_recent = pd.read_csv(DATA_DIR / 'gwl_karnataka_2021_2025.csv')
print(f"   GWL 2021-2025: {len(gwl_recent):,} records")

# Historical data 1991-2020
gwl_historical = pd.read_csv(DATA_DIR / 'gwl_karnataka_1991_2020.csv')
print(f"   GWL 1991-2020: {len(gwl_historical):,} records")

# Extraction data
extraction = pd.read_csv(DATA_DIR / 'karnataka_gw_extraction_2020.csv')
print(f"   Extraction 2020: {len(extraction):,} taluks")

# Combine recent and historical
gwl_all = pd.concat([gwl_historical, gwl_recent], ignore_index=True)
print(f"   Combined GWL: {len(gwl_all):,} total records")

# ============================================================
# 2. DATA PREPROCESSING
# ============================================================
print("\n2. DATA PREPROCESSING...")

# Parse dates
gwl_all['Date'] = pd.to_datetime(gwl_all['Data Acquisition Time'], format='%d-%m-%Y %H:%M', errors='coerce')
gwl_all['Year'] = gwl_all['Date'].dt.year
gwl_all['Month'] = gwl_all['Date'].dt.month
gwl_all['Quarter'] = gwl_all['Date'].dt.quarter

# Rename columns for clarity
gwl_all = gwl_all.rename(columns={
    'Groundwater Level Quarterly Manual (meter)': 'GWL_m',
    'District': 'District'
})

# Clean GWL values
gwl_all['GWL_m'] = pd.to_numeric(gwl_all['GWL_m'], errors='coerce')

# Remove outliers (GWL > 100m or < 0)
original_count = len(gwl_all)
gwl_all = gwl_all[(gwl_all['GWL_m'] >= 0) & (gwl_all['GWL_m'] <= 100)]
removed = original_count - len(gwl_all)
print(f"   Removed {removed:,} outliers (GWL < 0 or > 100m)")

# Check missing values
missing = gwl_all.isnull().sum()
print(f"   Missing GWL values: {missing['GWL_m']:,}")
print(f"   Missing dates: {missing['Date']:,}")

# Drop rows with missing critical values
gwl_clean = gwl_all.dropna(subset=['GWL_m', 'Date', 'District'])

# Karnataka renamed several districts and the CGWB export carries both spellings
# (Mysore/Mysuru, Gulbarga/Kalaburagi, Shimoga/Shivamogga), so the raw file has
# 33 labels for 28 real districts. Without this the EDA reported 33 districts,
# contradicting every other artefact, and the district charts drew the same
# district twice.
import sys as _sys
_sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_processor import canonical_district as _canon
_before = gwl_clean['District'].nunique()
gwl_clean['District'] = gwl_clean['District'].map(_canon)
print(f"   District names canonicalised: {_before} -> {gwl_clean['District'].nunique()}")
print(f"   Clean records: {len(gwl_clean):,}")

# ============================================================
# 3. DATASET SUMMARY
# ============================================================
print("\n3. DATASET SUMMARY")
print("-" * 40)

# Districts
districts = gwl_clean['District'].nunique()
print(f"   Districts covered: {districts}")

# Stations
stations = gwl_clean['Station'].nunique()
print(f"   Monitoring stations: {stations}")

# Date range
date_min = gwl_clean['Date'].min()
date_max = gwl_clean['Date'].max()
print(f"   Date range: {date_min.strftime('%Y-%m-%d')} to {date_max.strftime('%Y-%m-%d')}")

# GWL statistics
print(f"\n   Groundwater Level (meters):")
print(f"     Mean: {gwl_clean['GWL_m'].mean():.2f}")
print(f"     Std:  {gwl_clean['GWL_m'].std():.2f}")
print(f"     Min:  {gwl_clean['GWL_m'].min():.2f}")
print(f"     Max:  {gwl_clean['GWL_m'].max():.2f}")

# Save summary stats
summary = {
    'Total Records': len(gwl_clean),
    'Districts': districts,
    'Stations': stations,
    'Date Range': f"{date_min.strftime('%Y')} - {date_max.strftime('%Y')}",
    'Mean GWL (m)': round(gwl_clean['GWL_m'].mean(), 2),
    'Std GWL (m)': round(gwl_clean['GWL_m'].std(), 2),
}

# ============================================================
# 4. EDA VISUALIZATIONS
# ============================================================
print("\n4. GENERATING VISUALIZATIONS...")

# --- Plot 1: GWL Distribution ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(gwl_clean['GWL_m'], bins=50, color='steelblue', edgecolor='white', alpha=0.8)
axes[0].set_xlabel('Groundwater Level (meters below ground)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Distribution of Groundwater Levels in Karnataka')
axes[0].axvline(gwl_clean['GWL_m'].mean(), color='red', linestyle='--', label=f"Mean: {gwl_clean['GWL_m'].mean():.1f}m")
axes[0].legend()

axes[1].boxplot([gwl_clean['GWL_m'].dropna()], vert=True)
axes[1].set_ylabel('Groundwater Level (m)')
axes[1].set_title('Box Plot of GWL')
axes[1].set_xticklabels(['All Karnataka'])

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot1_gwl_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Saved: plot1_gwl_distribution.png")

# --- Plot 2: Yearly Trend ---
yearly = gwl_clean.groupby('Year')['GWL_m'].agg(['mean', 'std', 'count']).reset_index()
yearly = yearly[yearly['Year'] >= 1995]  # Focus on recent years

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(yearly['Year'], yearly['mean'], 'b-o', linewidth=2, markersize=6, label='Mean GWL')
ax.fill_between(yearly['Year'],
                yearly['mean'] - yearly['std'],
                yearly['mean'] + yearly['std'],
                alpha=0.2, color='blue', label='±1 Std Dev')
ax.set_xlabel('Year')
ax.set_ylabel('Mean Groundwater Level (m)')
ax.set_title('Yearly Trend of Groundwater Levels in Karnataka (1995-2025)')
ax.legend()
ax.invert_yaxis()  # Deeper = higher value
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot2_yearly_trend.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Saved: plot2_yearly_trend.png")

# --- Plot 3: Seasonal Pattern ---
seasonal = gwl_clean.groupby('Month')['GWL_m'].mean().reset_index()
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(seasonal['Month'], seasonal['GWL_m'], color='teal', edgecolor='white')
ax.set_xticks(range(1, 13))
ax.set_xticklabels(month_names)
ax.set_xlabel('Month')
ax.set_ylabel('Mean Groundwater Level (m)')
ax.set_title('Seasonal Pattern of Groundwater Levels')
ax.axhline(y=seasonal['GWL_m'].mean(), color='red', linestyle='--', label='Annual Mean')

# Highlight monsoon months (June-October)
monsoon_months = [6, 7, 8, 9, 10]
for idx, month in enumerate(seasonal['Month']):
    if month in monsoon_months:
        bars[idx].set_color('green')
ax.legend()

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot3_seasonal_pattern.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Saved: plot3_seasonal_pattern.png")

# --- Plot 4: District-wise Analysis ---
district_stats = gwl_clean.groupby('District')['GWL_m'].agg(['mean', 'std', 'count']).reset_index()
district_stats = district_stats.sort_values('mean', ascending=False).head(20)

fig, ax = plt.subplots(figsize=(14, 8))
colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(district_stats)))
bars = ax.barh(district_stats['District'], district_stats['mean'], color=colors, edgecolor='white')
ax.set_xlabel('Mean Groundwater Level (m)')
ax.set_ylabel('District')
ax.set_title('Top 20 Districts by Mean Groundwater Depth (Higher = More Depleted)')
ax.invert_yaxis()

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot4_district_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Saved: plot4_district_comparison.png")

# --- Plot 5: Correlation Matrix (Extraction Data) ---
numeric_cols = ['Total annual groundwater recharge', 'Annual Extractable Groundwater Resource',
                'Total Annual Extraction', 'Stage of GW extraction (%)']
extraction_numeric = extraction[numeric_cols].apply(pd.to_numeric, errors='coerce')

fig, ax = plt.subplots(figsize=(10, 8))
corr = extraction_numeric.corr()
sns.heatmap(corr, annot=True, cmap='RdYlBu_r', center=0,
            square=True, linewidths=0.5, ax=ax,
            xticklabels=['Recharge', 'Extractable', 'Extraction', 'Stage%'],
            yticklabels=['Recharge', 'Extractable', 'Extraction', 'Stage%'])
ax.set_title('Correlation Matrix of Groundwater Resources')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot5_correlation_matrix.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Saved: plot5_correlation_matrix.png")

# --- Plot 6: Extraction Category Distribution ---
category_counts = extraction['Categorization'].value_counts()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Pie chart
colors_cat = {'safe': 'green', 'semi-critical': 'yellow', 'critical': 'orange', 'over_exploited': 'red'}
cat_colors = [colors_cat.get(c.lower().replace('-', '_').replace(' ', '_'), 'gray') for c in category_counts.index]
axes[0].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%',
           colors=cat_colors, explode=[0.02]*len(category_counts))
axes[0].set_title('CGWB Categorization of Karnataka Taluks (2020)')

# Bar chart
axes[1].bar(category_counts.index, category_counts.values, color=cat_colors, edgecolor='white')
axes[1].set_xlabel('Category')
axes[1].set_ylabel('Number of Taluks')
axes[1].set_title('Distribution of Groundwater Extraction Categories')
for i, v in enumerate(category_counts.values):
    axes[1].text(i, v + 2, str(v), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot6_extraction_categories.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Saved: plot6_extraction_categories.png")

# --- Plot 7: Stage of Extraction by District ---
extraction['Stage of GW extraction (%)'] = pd.to_numeric(extraction['Stage of GW extraction (%)'], errors='coerce')
district_extraction = extraction.groupby('Name of District')['Stage of GW extraction (%)'].mean().sort_values(ascending=False).head(15)

fig, ax = plt.subplots(figsize=(14, 8))
colors = ['red' if v > 100 else 'orange' if v > 70 else 'yellow' if v > 50 else 'green'
          for v in district_extraction.values]
bars = ax.barh(district_extraction.index, district_extraction.values, color=colors, edgecolor='white')
ax.axvline(x=100, color='red', linestyle='--', linewidth=2, label='Over-exploitation threshold')
ax.axvline(x=70, color='orange', linestyle='--', linewidth=1.5, label='Critical threshold')
ax.set_xlabel('Stage of Groundwater Extraction (%)')
ax.set_ylabel('District')
ax.set_title('Top 15 Districts by Groundwater Extraction Stage')
ax.legend()
ax.invert_yaxis()

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot7_extraction_by_district.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Saved: plot7_extraction_by_district.png")

# --- Plot 8: Time Series for Critical Districts ---
critical_districts = ['Kolar', 'Chikballapur', 'Tumkur', 'Bangalore Urban', 'Ramanagara']
# Try to match district names
gwl_critical = gwl_clean[gwl_clean['District'].str.contains('|'.join(critical_districts), case=False, na=False)]

if len(gwl_critical) > 0:
    fig, ax = plt.subplots(figsize=(14, 7))
    for district in gwl_critical['District'].unique()[:5]:
        district_data = gwl_critical[gwl_critical['District'] == district]
        yearly_mean = district_data.groupby('Year')['GWL_m'].mean()
        ax.plot(yearly_mean.index, yearly_mean.values, 'o-', label=district, linewidth=2, markersize=4)

    ax.set_xlabel('Year')
    ax.set_ylabel('Mean Groundwater Level (m)')
    ax.set_title('Groundwater Level Trends in High-Risk Districts')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'plot8_critical_districts_trend.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   Saved: plot8_critical_districts_trend.png")

# --- Plot 9: Stations Map (Lat/Lon scatter) ---
stations_df = gwl_clean.groupby('Station').agg({
    'Latitude': 'first',
    'Longitude': 'first',
    'GWL_m': 'mean',
    'District': 'first'
}).reset_index()

fig, ax = plt.subplots(figsize=(12, 14))
scatter = ax.scatter(stations_df['Longitude'], stations_df['Latitude'],
                    c=stations_df['GWL_m'], cmap='RdYlGn_r',
                    s=30, alpha=0.7, edgecolors='white', linewidths=0.5)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Karnataka Groundwater Monitoring Stations\n(Color = Mean GWL Depth)')
cbar = plt.colorbar(scatter, ax=ax, shrink=0.6)
cbar.set_label('Mean GWL (m)')
ax.set_xlim([74, 78.5])
ax.set_ylim([11.5, 18.5])

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot9_stations_map.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Saved: plot9_stations_map.png")

# --- Plot 10: Missing Values Analysis ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Missing by year
yearly_missing = gwl_all.groupby('Year').apply(lambda x: x['GWL_m'].isnull().sum() / len(x) * 100)
axes[0].bar(yearly_missing.index, yearly_missing.values, color='coral', edgecolor='white')
axes[0].set_xlabel('Year')
axes[0].set_ylabel('Missing Values (%)')
axes[0].set_title('Missing GWL Values by Year')
axes[0].set_xlim([1990, 2027])

# Data completeness
completeness = {
    'GWL': gwl_all['GWL_m'].notna().sum() / len(gwl_all) * 100,
    'Date': gwl_all['Date'].notna().sum() / len(gwl_all) * 100,
    'District': gwl_all['District'].notna().sum() / len(gwl_all) * 100,
    'Lat/Lon': (gwl_all['Latitude'].notna() & gwl_all['Longitude'].notna()).sum() / len(gwl_all) * 100,
}
axes[1].bar(completeness.keys(), completeness.values(), color='seagreen', edgecolor='white')
axes[1].set_ylabel('Completeness (%)')
axes[1].set_title('Data Completeness by Field')
axes[1].set_ylim([0, 105])
for i, (k, v) in enumerate(completeness.items()):
    axes[1].text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot10_data_quality.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Saved: plot10_data_quality.png")

# ============================================================
# 5. SAVE PROCESSED DATA
# ============================================================
print("\n5. SAVING PROCESSED DATA...")

# Save clean GWL data
gwl_clean.to_csv(DATA_DIR / 'gwl_karnataka_clean.csv', index=False)
print(f"   Saved: gwl_karnataka_clean.csv ({len(gwl_clean):,} records)")

# Save district summary
district_summary = gwl_clean.groupby('District').agg({
    'GWL_m': ['mean', 'std', 'min', 'max', 'count'],
    'Station': 'nunique',
    'Latitude': 'mean',
    'Longitude': 'mean'
}).round(2)
district_summary.columns = ['Mean_GWL', 'Std_GWL', 'Min_GWL', 'Max_GWL', 'Records', 'Stations', 'Lat', 'Lon']
district_summary.to_csv(DATA_DIR / 'district_summary.csv')
print(f"   Saved: district_summary.csv ({len(district_summary)} districts)")

# ============================================================
# 6. SUMMARY STATISTICS
# ============================================================
print("\n" + "="*60)
print("SUMMARY FOR PRESENTATION")
print("="*60)

print(f"""
DATASET OVERVIEW:
-----------------
• Source: Central Ground Water Board (CGWB), National Water Data Portal
• Total Records: {len(gwl_clean):,}
• Time Period: 1991 - 2025 ({date_max.year - date_min.year} years)
• Districts: {districts}
• Monitoring Stations: {stations}
• Features: Station, District, Block, Village, Lat/Lon, Date, GWL

GROUNDWATER LEVEL STATISTICS:
-----------------------------
• Mean Depth: {gwl_clean['GWL_m'].mean():.2f} meters
• Std Deviation: {gwl_clean['GWL_m'].std():.2f} meters
• Range: {gwl_clean['GWL_m'].min():.2f} - {gwl_clean['GWL_m'].max():.2f} meters

EXTRACTION DATA (2020):
-----------------------
• Taluks Assessed: {len(extraction)}
• Over-exploited: {(extraction['Categorization'].str.lower() == 'over_exploited').sum()} taluks
• Critical: {(extraction['Categorization'].str.lower() == 'critical').sum()} taluks
• Semi-critical: {(extraction['Categorization'].str.lower() == 'semi-critical').sum()} taluks
• Safe: {(extraction['Categorization'].str.lower() == 'safe').sum()} taluks

KEY OBSERVATIONS:
-----------------
1. Groundwater levels show clear seasonal patterns - shallower during monsoon
2. Long-term trend shows gradual deepening over decades
3. Eastern districts (Kolar, Chikballapur) show highest depletion
4. ~{((extraction['Categorization'].str.lower() == 'over_exploited').sum() + (extraction['Categorization'].str.lower() == 'critical').sum()) / len(extraction) * 100:.0f}% of taluks are critical/over-exploited

VISUALIZATIONS GENERATED: 10 plots saved to outputs/eda_plots/
""")

print("="*60)
print("EDA COMPLETE!")
print("="*60)
