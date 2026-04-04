# Landsat Summer Heat Metrics Pipeline

This project builds annual (2020-2025) summer (June-August) Landsat composites and exports:

- Tract-level CSV summaries for LST, NDVI, and NDBI
- Yearly multi-band GeoTIFFs (LST_C, NDVI, NDBI)
- Yearly single-band GeoTIFFs for each index/band

The script targets Lincoln Nebraska defined by census tracts in a GeoJSON file.

## Project Structure

```text
landsat/
	data/
		raw/
			cleanedCensusTracts.geojson
	scripts/
		landsat_tract_pipeline.py
	README.md
```

## Requirements

- Python environment (project uses `.venv`)
- Google Earth Engine account access
- A Google Cloud project enabled for Earth Engine API

Python packages used:

- earthengine-api
- geemap
- geopandas

## Setup

1. Install dependencies in the project venv:

```powershell
-m pip install earthengine-api geemap geopandas
```

2. Set your Earth Engine project ID in `scripts/landsat_tract_pipeline.py`:

```python
GEE_PROJECT_ID = "heat-islands-project"
```

3. Make sure your user has permission on that Google Cloud project:

- Role: `roles/serviceusage.serviceUsageConsumer`
- Earth Engine API enabled in the project

4. Place GeoJSON at:

`data/raw/cleanedCensusTracts.geojson`

## Run the Pipeline

Run:

```powershell
scripts/landsat_tract_pipeline.py
```

On first run, Earth Engine may prompt browser authentication.

## What Gets Exported

Current main block submits:

- CSV exports: years 2020 to 2025
- Separate-band GeoTIFF exports: years 2020 to 2025
- Multi-band GeoTIFF exports are available but currently commented out in main

Export destination:

- Google Drive folder: `GEE_Landsat_Lincoln`

Notes:

- If a year has no matching imagery, that year is skipped.

## Viewing Queue and Status

Use Earth Engine Code Editor Tasks tab:

- https://code.earthengine.google.com

Task statuses include `READY`, `RUNNING`, `COMPLETED`, and `FAILED`.

## Map Preview

The script includes `preview_map(...)` for interactive use.

In notebook/interactive Python:

```python
from scripts.landsat_tract_pipeline import initialize_earth_engine, load_tracts, preview_map

initialize_earth_engine()
_, tracts_fc, study_area = load_tracts()
preview_map(2020, study_area, tracts_fc)
```

## Troubleshooting

- `pip` not recognized in PowerShell:
	- Use `python -m pip` with the venv interpreter path shown above.
- `ee.Initialize: no project found`:
	- Set `GEE_PROJECT_ID` and initialize with `ee.Initialize(project=...)`.
- `Caller does not have required permission to use project ...`:
	- Add the Service Usage Consumer role in IAM and wait a few minutes for propagation.