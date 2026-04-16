import geopandas as gpd
import pandas as pd

# -----------------------------
# 1. Load datasets
# -----------------------------
gdf = gpd.read_file("cleanedCensusTracts.geojson")
acs = pd.read_csv("acs_lancaster_tracts_2020_now_combined.csv")
summer = pd.read_csv("lincoln_tract_summer_stats_final.csv")

# -----------------------------
# 2. Inspect columns
# -----------------------------
print("GeoJSON columns:", gdf.columns.tolist())
print("ACS columns:", acs.columns.tolist())
print("Summer columns:", summer.columns.tolist())

# -----------------------------
# 3. Standardize GEOID fields
# -----------------------------
gdf["GEOID"] = gdf["GEOID"].astype(str).str.replace(".0", "", regex=False)
acs["GEOID"] = acs["GEOID"].astype(str).str.replace(".0", "", regex=False)
summer["GEOID"] = summer["GEOID"].astype(str).str.replace(".0", "", regex=False)

# Make sure year fields are integers
acs["acs_release_year"] = pd.to_numeric(acs["acs_release_year"], errors="coerce").astype("Int64")
summer["year"] = pd.to_numeric(summer["year"], errors="coerce").astype("Int64")

# -----------------------------
# 4. Match heat years to ACS years
# -----------------------------
# 2025 heat uses 2024 ACS as the closest available ACS release
summer["acs_match_year"] = summer["year"].apply(lambda y: 2024 if y == 2025 else y)

print("\nHeat year to ACS match mapping:")
print(summer[["year", "acs_match_year"]].drop_duplicates().sort_values("year"))

# -----------------------------
# 5. Merge summer + ACS first
# -----------------------------
master_tabular = summer.merge(
    acs,
    left_on=["GEOID", "acs_match_year"],
    right_on=["GEOID", "acs_release_year"],
    how="left"
)

# -----------------------------
# 6. Merge with GeoJSON
# -----------------------------
master = gdf.merge(master_tabular, on="GEOID", how="left")

# -----------------------------
# 7. Validate merge
# -----------------------------
print("\nFinal shape:", master.shape)

key_missing = master[[
    "GEOID", "year", "acs_match_year", "median_household_income",
    "poverty_rate_pct", "renter_occupied_pct", "LST_C", "NDVI", "NDBI"
]].isna().sum()

print("\nMissing values in key columns:")
print(key_missing)

# Check rows where ACS did not merge
acs_missing = master[master["median_household_income"].isna()]
print("\nRows missing ACS match:", len(acs_missing))

if len(acs_missing) > 0:
    print("\nSample unmatched rows:")
    print(acs_missing[["GEOID", "year", "acs_match_year"]].head(10))

# Optional: check row counts by year
print("\nRow counts by year:")
print(master["year"].value_counts(dropna=False).sort_index())

# -----------------------------
# 8. Save outputs
# -----------------------------
master.to_file("master_2020_2025.geojson", driver="GeoJSON")
master.drop(columns="geometry").to_csv("master_2020_2025.csv", index=False)

print("\nMaster dataset created successfully!")