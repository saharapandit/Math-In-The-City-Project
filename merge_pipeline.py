import geopandas as gpd
import pandas as pd


# 1. Load datasets

gdf = gpd.read_file("cleanedCensusTracts.geojson")
acs = pd.read_csv("acs_lancaster_tracts_2020.csv")
summer = pd.read_csv("lincoln_tract_summer_stats_2020.csv")


# 2. Inspect columns

print("GeoJSON columns:", gdf.columns)
print("ACS columns:", acs.columns)
print("Summer columns:", summer.columns)


# 3. Standardize GEOID


# GeoJSON (handle decimals if present)
gdf["GEOID"] = gdf["GEOID"].astype(str)
gdf["GEOID"] = gdf["GEOID"].str.replace(".0", "", regex=False)

# ACS
acs["GEOID"] = acs["GEOID"].astype(str)

# Summer stats (this may be different!)
# Check if it's named GEOID, tract, or something else
if "GEOID" in summer.columns:
    summer["GEOID"] = summer["GEOID"].astype(str)
elif "tract" in summer.columns:
    summer["GEOID"] = summer["tract"].astype(str)
elif "TRACTCE" in summer.columns:
    # Combine if needed
    summer["GEOID"] = summer["TRACTCE"].astype(str)

# Remove decimals if needed
summer["GEOID"] = summer["GEOID"].str.replace(".0", "", regex=False)


# 4. Merge step-by-step


# Merge ACS first
master = gdf.merge(acs, on="GEOID", how="left")

# Merge summer stats (LST)
master = master.merge(summer, on="GEOID", how="left")


# 5. Validate merge

print("Final shape:", master.shape)
print("Missing values:\n", master.isna().sum())

# Check unmatched tracts
missing = master[master.isna().any(axis=1)]
print("Unmatched rows:", len(missing))


# 6. Save master dataset


# Spatial version
master.to_file("master_2020.geojson", driver="GeoJSON")

# Non-spatial version (for modeling)
master.drop(columns="geometry").to_csv("master_2020.csv", index=False)

print("Master dataset created successfully!")