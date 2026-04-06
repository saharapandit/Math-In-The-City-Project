"""
acs_heat_vulnerability_2020_now_with_geojson.py

Purpose:
    Pull ACS 5-year tract-level variables for Lancaster County, Nebraska
    for heat-vulnerability analysis from 2020 through the latest available
    ACS 5-year release, then merge them with the cleaned census tract GeoJSON
    hosted on GitHub.

What "2020-now" means here:
    2020 ACS 5-year = 2016-2020
    2021 ACS 5-year = 2017-2021
    2022 ACS 5-year = 2018-2022
    2023 ACS 5-year = 2019-2023
    2024 ACS 5-year = 2020-2024

Outputs:
    - One CSV per ACS release year
    - One combined CSV with all years stacked together
    - One merged GeoJSON per ACS release year
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

import pandas as pd
import requests
import geopandas as gpd



# Config


STATE_FIPS = "31"      # Nebraska
COUNTY_FIPS = "109"    # Lancaster County
DEFAULT_YEARS = [2020, 2021, 2022, 2023, 2024]
BASE_URL = "https://api.census.gov/data"
OUTPUT_DIR = Path("output_acs_2020_now")

# Raw GitHub URL for your cleaned tract boundaries
GEOJSON_URL = "https://raw.githubusercontent.com/saharapandit/Math-In-The-City-Project/main/Census%20Tracts%20Cleaning/Data/cleanedCensusTracts.geojson"



# ACS variables


ACS_VARS = [
    "NAME",

    # Poverty
    "B17001_001E",
    "B17001_002E",

    # Median household income
    "B19013_001E",

    # Tenure
    "B25003_001E",
    "B25003_003E",

    # Total population + age 65+
    "B01001_001E",
    "B01001_020E",
    "B01001_021E",
    "B01001_022E",
    "B01001_023E",
    "B01001_024E",
    "B01001_025E",
    "B01001_044E",
    "B01001_045E",
    "B01001_046E",
    "B01001_047E",
    "B01001_048E",
    "B01001_049E",

    # Elderly living alone
    "B09020_001E",
    "B09020_015E",
    "B09020_018E",

    # Disability
    "B18101_001E",
    "B18101_004E",
    "B18101_007E",
    "B18101_010E",
    "B18101_013E",
    "B18101_016E",
    "B18101_019E",
    "B18101_023E",
    "B18101_026E",
    "B18101_029E",
    "B18101_032E",
    "B18101_035E",
    "B18101_038E",

    # Race
    "B02001_001E",
    "B02001_002E",

    # Limited English-speaking households
    "C16002_001E",
    "C16002_004E",
    "C16002_007E",
    "C16002_010E",
    "C16002_013E",
]



# Helper Functions


def safe_to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def pct(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denom = denominator.where(denominator != 0)
    return ((numerator / denom) * 100).astype("float64")


def validate_years(years: Iterable[int]) -> List[int]:
    cleaned = []
    for y in years:
        y = int(y)
        if y < 2020:
            raise ValueError("This script is set up for ACS release years 2020 through 2024.")
        cleaned.append(y)
    return cleaned



# API pull


def fetch_acs_tract_data(year: int, api_key: str) -> pd.DataFrame:
    url = f"{BASE_URL}/{year}/acs/acs5"
    params = {
        "get": ",".join(ACS_VARS),
        "for": "tract:*",
        "in": f"state:{STATE_FIPS} county:{COUNTY_FIPS}",
        "key": api_key,
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])

    non_numeric = {"NAME", "state", "county", "tract"}
    for col in df.columns:
        if col not in non_numeric:
            df[col] = safe_to_numeric(df[col])

    return df



# Derived variables


def compute_derived_variables(df: pd.DataFrame, year: int) -> pd.DataFrame:
    out = df.copy()

    out["GEOID"] = out["state"] + out["county"] + out["tract"]
    out["acs_release_year"] = year
    out["acs_window"] = f"{year - 4}-{year}"

    age_65_plus_cols = [
        "B01001_020E", "B01001_021E", "B01001_022E",
        "B01001_023E", "B01001_024E", "B01001_025E",
        "B01001_044E", "B01001_045E", "B01001_046E",
        "B01001_047E", "B01001_048E", "B01001_049E",
    ]
    out["count_age_65_plus"] = out[age_65_plus_cols].sum(axis=1)

    out["count_elderly_living_alone"] = out["B09020_015E"] + out["B09020_018E"]

    disability_cols = [
        "B18101_004E", "B18101_007E", "B18101_010E",
        "B18101_013E", "B18101_016E", "B18101_019E",
        "B18101_023E", "B18101_026E", "B18101_029E",
        "B18101_032E", "B18101_035E", "B18101_038E",
    ]
    out["count_disabled"] = out[disability_cols].sum(axis=1)

    out["count_nonwhite"] = out["B02001_001E"] - out["B02001_002E"]

    lep_cols = ["C16002_004E", "C16002_007E", "C16002_010E", "C16002_013E"]
    out["count_limited_english_households"] = out[lep_cols].sum(axis=1)

    out["median_household_income"] = out["B19013_001E"]
    out["poverty_rate_pct"] = pct(out["B17001_002E"], out["B17001_001E"])
    out["renter_occupied_pct"] = pct(out["B25003_003E"], out["B25003_001E"])
    out["age_65_plus_pct"] = pct(out["count_age_65_plus"], out["B01001_001E"])
    out["elderly_living_alone_pct"] = pct(out["count_elderly_living_alone"], out["B09020_001E"])
    out["disability_pct"] = pct(out["count_disabled"], out["B18101_001E"])
    out["nonwhite_pct"] = pct(out["count_nonwhite"], out["B02001_001E"])
    out["limited_english_households_pct"] = pct(
        out["count_limited_english_households"],
        out["C16002_001E"]
    )

    keep_cols = [
        "acs_release_year",
        "acs_window",
        "GEOID",
        "NAME",
        "median_household_income",
        "poverty_rate_pct",
        "renter_occupied_pct",
        "age_65_plus_pct",
        "elderly_living_alone_pct",
        "disability_pct",
        "nonwhite_pct",
        "limited_english_households_pct",
        "count_age_65_plus",
        "count_elderly_living_alone",
        "count_disabled",
        "count_nonwhite",
        "count_limited_english_households",
    ]

    out = out[keep_cols].copy()

    pct_cols = [
        "poverty_rate_pct",
        "renter_occupied_pct",
        "age_65_plus_pct",
        "elderly_living_alone_pct",
        "disability_pct",
        "nonwhite_pct",
        "limited_english_households_pct",
    ]
    out[pct_cols] = out[pct_cols].round(2)

    return out



# Geography merge


def load_geojson_from_github(url: str) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(url)

    if "GEOID" not in gdf.columns:
        possible_geoid_cols = [col for col in gdf.columns if "geoid" in col.lower()]
        raise ValueError(
            f"No exact 'GEOID' column found in GeoJSON. Found similar columns: {possible_geoid_cols}"
        )

    gdf["GEOID"] = gdf["GEOID"].astype(str)
    return gdf


def merge_acs_with_geojson(acs_df: pd.DataFrame, tract_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    acs_df = acs_df.copy()
    acs_df["GEOID"] = acs_df["GEOID"].astype(str)

    merged = tract_gdf.merge(acs_df, on="GEOID", how="left")
    return merged


# --------------------------------------------------
# Save helpers
# --------------------------------------------------

def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved CSV: {path}")


def save_geojson(gdf: gpd.GeoDataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(path, driver="GeoJSON")
    print(f"Saved GeoJSON: {path}")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pull ACS tract-level heat vulnerability variables and merge with GitHub GeoJSON."
    )
    parser.add_argument("--api_key", required=True, help="Your Census API key.")
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=DEFAULT_YEARS,
        help="ACS release years to pull. Default: 2020 2021 2022 2023 2024"
    )
    args = parser.parse_args()

    years = validate_years(args.years)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading cleaned census tract GeoJSON from GitHub...")
    tract_gdf = load_geojson_from_github(GEOJSON_URL)

    all_years = []

    for year in years:
        print(f"\nPulling ACS 5-year tract data for release year {year}...")

        try:
            raw_df = fetch_acs_tract_data(year=year, api_key=args.api_key)
            final_df = compute_derived_variables(raw_df, year=year)

            csv_path = OUTPUT_DIR / f"acs_lancaster_tracts_{year}.csv"
            save_csv(final_df, csv_path)

            merged_gdf = merge_acs_with_geojson(final_df, tract_gdf)
            geojson_path = OUTPUT_DIR / f"acs_lancaster_tracts_{year}_merged.geojson"
            save_geojson(merged_gdf, geojson_path)

            all_years.append(final_df)

        except requests.HTTPError as e:
            print(f"HTTP error for year {year}: {e}")
            if e.response is not None:
                print("Response text:", e.response.text)
        except Exception as e:
            print(f"Error for year {year}: {e}")

    if all_years:
        combined = pd.concat(all_years, ignore_index=True)
        combined_csv = OUTPUT_DIR / "acs_lancaster_tracts_2020_now_combined.csv"
        save_csv(combined, combined_csv)

        print("\nDone.")
        print("Output folder:", OUTPUT_DIR.resolve())
    else:
        print("\nNo files were created because all requests failed.")


if __name__ == "__main__":
    main()