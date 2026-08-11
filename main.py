# ============================================================
# PROJECT 1: Solar Potential Analysis for Northern Virginia
# Author: [Your Name]
# Date: [Today's Date]
# Data Source: NREL PVWatts V8 API (developer.nlr.gov)
# ============================================================

import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os
from config import API_KEY

# -------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------
SYSTEM_CAPACITY_KW = 4
PANEL_AZIMUTH = 180
PANEL_TILT = 38
ARRAY_TYPE = 1
MODULE_TYPE = 0
SYSTEM_LOSSES_PCT = 14
CO2_KG_PER_KWH = 0.386
BASE_URL = "https://developer.nlr.gov/api/pvwatts/v8.json"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

os.makedirs("results", exist_ok=True)

# -------------------------------------------------------
# LOCATIONS — using lat/lon instead of address
# (NREL removed address support in February 2025)
# -------------------------------------------------------
LOCATIONS = [
    {"name": "Centreville",  "lat": 38.8404, "lon": -77.4291},
    {"name": "Manassas",     "lat": 38.7509, "lon": -77.4753},
    {"name": "Reston",       "lat": 38.9687, "lon": -77.3411},
    {"name": "Fairfax",      "lat": 38.8462, "lon": -77.3064},
    {"name": "Arlington",    "lat": 38.8816, "lon": -77.0910},
]

# -------------------------------------------------------
# FUNCTION: get_solar_data
# -------------------------------------------------------
def get_solar_data(name, lat, lon):
    params = {
        "api_key": API_KEY,
        "system_capacity": SYSTEM_CAPACITY_KW,
        "lat": lat,
        "lon": lon,
        "azimuth": PANEL_AZIMUTH,
        "tilt": PANEL_TILT,
        "array_type": ARRAY_TYPE,
        "module_type": MODULE_TYPE,
        "losses": SYSTEM_LOSSES_PCT,
        "timeframe": "monthly"
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data.get("errors"):
            print(f"  API error for {name}: {data['errors']}")
            return None
        return data["outputs"]["ac_monthly"]
    except requests.exceptions.Timeout:
        print(f"  Request timed out for {name}.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"  HTTP error for {name}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  Connection error for {name}: {e}")
        return None

# -------------------------------------------------------
# DATA COLLECTION
# -------------------------------------------------------
print("=" * 60)
print("  NREL PVWatts Solar Analysis — Northern Virginia")
print("=" * 60)
print(f"\nSystem size: {SYSTEM_CAPACITY_KW} kW | Azimuth: {PANEL_AZIMUTH}° | Tilt: {PANEL_TILT}°")
print(f"Analyzing {len(LOCATIONS)} locations...\n")

all_results = {}

for location in LOCATIONS:
    name = location["name"]
    lat = location["lat"]
    lon = location["lon"]
    print(f"  Fetching data for {name}...", end="")
    monthly_data = get_solar_data(name, lat, lon)
    if monthly_data is not None:
        all_results[name] = monthly_data
        print(f" Done. Annual: {sum(monthly_data):,.0f} kWh")
    else:
        print(f" FAILED — skipping")

print(f"\nData retrieved for {len(all_results)} of {len(LOCATIONS)} locations.")

if not all_results:
    print("\nNo data retrieved. Check API key and internet connection.")
    exit()

# -------------------------------------------------------
# BUILD DATAFRAME
# -------------------------------------------------------
df = pd.DataFrame(all_results, index=MONTHS)
df.index.name = "Month"
print("\n--- Monthly Output Table (kWh) ---")
print(df.to_string())
annual_totals = df.sum()

# -------------------------------------------------------
# CHART 1: Monthly Grouped Bar Chart
# -------------------------------------------------------
print("\nCreating charts...")
plt.style.use("seaborn-v0_8-whitegrid")
colors = ["#2196F3", "#FF9800", "#4CAF50", "#9C27B0", "#F44336"]
fig, ax = plt.subplots(figsize=(14, 7))
num_locations = len(all_results)
x = np.arange(len(MONTHS))
bar_width = 0.8 / num_locations

for i, (location_name, monthly_values) in enumerate(all_results.items()):
    offset = (i - num_locations / 2 + 0.5) * bar_width
    ax.bar(x + offset, monthly_values, bar_width,
           label=location_name, color=colors[i % len(colors)],
           alpha=0.85, edgecolor="white", linewidth=0.5)

ax.set_xlabel("Month", fontsize=12, labelpad=10)
ax.set_ylabel("Energy Output (kWh)", fontsize=12, labelpad=10)
ax.set_title(
    f"Monthly Solar Energy Output — Northern Virginia\n"
    f"{SYSTEM_CAPACITY_KW} kW System | South-Facing | Fixed Mount",
    fontsize=14, fontweight="bold", pad=15)
ax.set_xticks(x)
ax.set_xticklabels(MONTHS, fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda val, _: f"{val:,.0f}"))
ax.legend(title="Location", fontsize=10, title_fontsize=11,
          loc="upper right", framealpha=0.9)
fig.text(0.5, -0.02,
         "Data source: NREL PVWatts V8 API | EPA eGRID 2022 emissions factors",
         ha="center", fontsize=9, color="gray")
plt.tight_layout()
chart1_path = os.path.join("results", "monthly_output_comparison.png")
plt.savefig(chart1_path, dpi=150, bbox_inches="tight")
print(f"  Saved: {chart1_path}")
plt.close()

# -------------------------------------------------------
# CHART 2: Annual Totals Horizontal Bar Chart
# -------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))
sorted_pairs = sorted(zip(annual_totals.values, annual_totals.index), reverse=True)
sorted_values, sorted_names = zip(*sorted_pairs)
bars = ax.barh(sorted_names, sorted_values,
               color=colors[:len(sorted_names)], alpha=0.85,
               edgecolor="white", linewidth=0.5)
for bar, value in zip(bars, sorted_values):
    ax.text(bar.get_width() + 30,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,.0f} kWh", va="center", fontsize=10, color="#333333")
ax.set_xlabel("Annual Energy Output (kWh)", fontsize=12, labelpad=10)
ax.set_title(
    f"Annual Solar Output by Location — Northern Virginia\n{SYSTEM_CAPACITY_KW} kW System",
    fontsize=14, fontweight="bold", pad=15)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda val, _: f"{val:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.text(0.5, -0.02, "Data source: NREL PVWatts V8 API",
         ha="center", fontsize=9, color="gray")
plt.tight_layout()
chart2_path = os.path.join("results", "annual_totals_comparison.png")
plt.savefig(chart2_path, dpi=150, bbox_inches="tight")
print(f"  Saved: {chart2_path}")
plt.close()

# -------------------------------------------------------
# FINAL REPORT
# -------------------------------------------------------
print("\n")
print("=" * 60)
print("  FINAL SUMMARY REPORT")
print("=" * 60)
print(f"\n  System: {SYSTEM_CAPACITY_KW} kW rooftop solar, south-facing, fixed mount")
print(f"  Analysis area: Northern Virginia\n")
print(f"  {'Location':<15} {'Annual kWh':>12} {'CO₂ Offset (lbs)':>18} {'Avg Monthly':>14}")
print("  " + "-" * 61)
for location_name, total in annual_totals.items():
    co2_lbs = total * CO2_KG_PER_KWH * 2.205
    avg_monthly = total / 12
    print(f"  {location_name:<15} {total:>12,.0f} {co2_lbs:>18,.0f} {avg_monthly:>14,.1f}")
best = annual_totals.idxmax()
worst = annual_totals.idxmin()
diff = annual_totals.max() - annual_totals.min()
print(f"\n  Best location:   {best} ({annual_totals[best]:,.0f} kWh/year)")
print(f"  Lowest location: {worst} ({annual_totals[worst]:,.0f} kWh/year)")
print(f"  Range: {diff:,.0f} kWh/year between best and lowest location")
print(f"\n  Charts saved to: results/")
print("=" * 60)
print("  Analysis complete.")
print("=" * 60)