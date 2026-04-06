# ACS Heat Vulnerability Data Extraction

## Overview

This script (`acs_extraction_GJ.py`) pulls American Community Survey (ACS) 5-year tract-level demographic and socioeconomic variables for **Lancaster County, Nebraska** for heat-vulnerability analysis. It retrieves data across multiple ACS releases (2020–2024), merges the data with census tract GeoJSON boundaries, and outputs both CSV and GeoJSON files for further analysis.

### What "2020-now" Means

The script pulls data from five consecutive ACS 5-year releases:

- **2020 ACS 5-year**: 2016–2020 data
- **2021 ACS 5-year**: 2017–2021 data
- **2022 ACS 5-year**: 2018–2022 data
- **2023 ACS 5-year**: 2019–2023 data
- **2024 ACS 5-year**: 2020–2024 data

---

## Prerequisites

### System Requirements

- Python 3.8+
- Internet connection (for Census API and GitHub GeoJSON access)

### Python Packages

The script requires the following packages:

- **pandas**: Data manipulation and CSV handling
- **requests**: HTTP requests to the Census API
- **geopandas**: Geospatial data handling and GeoJSON processing

### Census API Key

You need a valid Census Bureau API key to retrieve data. Obtain one for free at:
[https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)

---

## Installation & Setup

### 1. Clone or Download the Script

Place `acs_extraction_GJ.py` in your working directory.

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install pandas requests geopandas
```

---

## Usage

### Basic Command

```bash
python acs_extraction_GJ.py --api_key YOUR_CENSUS_API_KEY
```

Replace `YOUR_CENSUS_API_KEY` with your Census Bureau API key.

### Advanced Options

#### Pull Specific Years

By default, the script pulls data for 2020–2024. To pull specific years:

```bash
python acs_extraction_GJ.py --api_key YOUR_API_KEY --years 2022 2023 2024
```

#### Example with Full Parameters

```bash
python acs_extraction_GJ.py --api_key ca1e0fbbcbff872a3405a3fde2c2dd1b9d07a1fb --years 2020 2021 2022
```

---

## Output Files

The script creates an `output_acs_2020_now/` directory (by default) containing:

### Per-Year Outputs

For each requested year, the script generates:

- **`acs_lancaster_tracts_YYYY.csv`**: CSV with demographic variables for year YYYY
- **`acs_lancaster_tracts_YYYY_merged.geojson`**: GeoJSON with census tracts and merged ACS variables

Example files for 2024:
- `acs_lancaster_tracts_2024.csv`
- `acs_lancaster_tracts_2024_merged.geojson`

### Combined Output

- **`acs_lancaster_tracts_2020_now_combined.csv`**: All years stacked together (useful for time-series analysis)

---

## Variables Explained

The script extracts and computes the following variables:

### Metadata

- **acs_release_year**: The ACS release year (e.g., 2024)
- **acs_window**: The data collection window (e.g., "2020-2024")
- **GEOID**: Census tract geographic identifier
- **NAME**: Census tract name

### Demographic Indicators

#### Poverty & Income

- **poverty_rate_pct**: Percentage of population below poverty line
- **median_household_income**: Median household income in dollars

#### Housing

- **renter_occupied_pct**: Percentage of renter-occupied housing units

#### Age & Elderly

- **age_65_plus_pct**: Percentage of population aged 65+
- **count_age_65_plus**: Count of population aged 65+
- **elderly_living_alone_pct**: Percentage of elderly persons living alone
- **count_elderly_living_alone**: Count of elderly persons living alone

#### Disability

- **disability_pct**: Percentage of population with disabilities
- **count_disabled**: Count of population with disabilities

#### Race & Ethnicity

- **nonwhite_pct**: Percentage of non-white population
- **count_nonwhite**: Count of non-white population

#### Language Access

- **limited_english_households_pct**: Percentage of households with limited English proficiency
- **count_limited_english_households**: Count of households with limited English proficiency

---

## Data Sources

- **Census Data**: U.S. Census Bureau American Community Survey (ACS) 5-year estimates via [https://api.census.gov/data](https://api.census.gov/data)
- **Geography**: Cleaned census tract boundaries hosted at [GitHub: Math-In-The-City-Project](https://raw.githubusercontent.com/saharapandit/Math-In-The-City-Project/main/Census%20Tracts%20Cleaning/Data/cleanedCensusTracts.geojson)

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"

**Solution**: Install required packages:
```bash
pip install pandas requests geopandas
```

### "HTTP error for year YYYY"

**Possible causes**:
- Invalid Census API key
- Census API service down
- Network connectivity issues

**Solution**: Verify your API key on the [Census API website](https://api.census.gov/data/key_signup.html) and check your internet connection.

### "No exact 'GEOID' column found in GeoJSON"

**Cause**: The GitHub-hosted GeoJSON does not have the expected column structure.

**Solution**: Check that the GeoJSON URL in the script still contains a `GEOID` column. Update the URL if the source has changed.

### Script crashes with percentage calculation errors

**Cause**: Missing or zero values in denominators.

**Solution**: The script now handles these gracefully by converting zero denominators to NaN, which propagates through percentage calculations.

---

## Configuration

### Modify Default Years

Edit the `DEFAULT_YEARS` variable in the script:

```python
DEFAULT_YEARS = [2020, 2021, 2022, 2023, 2024]
```

### Change Output Directory

Edit the `OUTPUT_DIR` variable:

```python
OUTPUT_DIR = Path("output_acs_2020_now")
```

### Change Geography (State/County)

Edit the `STATE_FIPS` and `COUNTY_FIPS` variables:

```python
STATE_FIPS = "31"      # Nebraska
COUNTY_FIPS = "109"    # Lancaster County
```

To find FIPS codes for other counties, visit the [U.S. Census Bureau FIPS page](https://www.census.gov/library/reference/code-lists/ansi.html).

---

## Advanced Usage

### Filter Variables

The `ACS_VARS` list contains all requested Census variable codes. To use a subset, edit the list:

```python
ACS_VARS = [
    "NAME",
    "B17001_001E",  # Total population for poverty
    "B17001_002E",  # Population below poverty
    "B19013_001E",  # Median household income
]
```

### Custom Derived Variables

Add new calculations in the `compute_derived_variables()` function. For example:

```python
out["custom_metric"] = (out["col1"] + out["col2"]) / out["col3"]
```

---

## Data Quality Notes

- **Missing Values**: Census tracts with missing estimates will appear as NaN in outputs
- **Suppression**: The Census Bureau may suppress certain small-area estimates for privacy; these appear as NaN
- **Rounding**: Percentages are rounded to 2 decimal places

---

## License & Attribution

This script uses publicly available U.S. Census Bureau data. Census data is in the public domain. 

GeometryJSON source: [Math-In-The-City-Project GitHub](https://github.com/saharapandit/Math-In-The-City-Project) - verify applicable license for that repository.

---

## Questions or Issues?

For Census API support:
- Visit [https://api.census.gov/data](https://api.census.gov/data)
- Check Census Bureau documentation

For GIS/GeoJSON issues:
- Review [GeoPandas documentation](https://geopandas.org/)
- Verify GeoJSON format with [GeoJSON validators](https://geojsonlint.com/)

---

**Last Updated**: April 2026
