import json
import os
import ee
import geemap
import geopandas as gpd


# 1. EARTH ENGINE INITIALIZATION

GEE_PROJECT_ID = "heat-islands-project"

def initialize_earth_engine():
    try:
        ee.Initialize(project=GEE_PROJECT_ID)
        print("Earth Engine initialized successfully.")
    except Exception:
        print("Authenticating Earth Engine...")
        ee.Authenticate()
        ee.Initialize(project=GEE_PROJECT_ID)
        print("Earth Engine authenticated and initialized successfully.")


# 2. PROJECT PATHS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")


GEOJSON_PATH = os.path.join(RAW_DATA_DIR, "cleanedCensusTracts.geojson")


# 3. LOAD GEOJSON INTO EARTH ENGINE

def load_tracts():
    print(f"Loading GeoJSON from: {GEOJSON_PATH}")

    if not os.path.exists(GEOJSON_PATH):
        raise FileNotFoundError(f"Could not find file: {GEOJSON_PATH}")

    try:
        gdf = gpd.read_file(GEOJSON_PATH)
        print(f"Loaded {len(gdf)} tract features.")
        tracts_fc = geemap.geopandas_to_ee(gdf)
        study_area = tracts_fc.geometry()
        print("Converted GeoJSON to Earth Engine FeatureCollection.")
        return gdf, tracts_fc, study_area
    except Exception as e:
        raise RuntimeError(f"Error loading GeoJSON: {e}")


# 4. LANDSAT CLOUD MASKING

def mask_landsat_c2_l2(image):
    qa = image.select("QA_PIXEL")

    dilated_cloud = qa.bitwiseAnd(1 << 1).eq(0)
    cirrus = qa.bitwiseAnd(1 << 2).eq(0)
    cloud = qa.bitwiseAnd(1 << 3).eq(0)
    cloud_shadow = qa.bitwiseAnd(1 << 4).eq(0)

    mask = dilated_cloud.And(cirrus).And(cloud).And(cloud_shadow)

    return image.updateMask(mask)


# 5. SCALE LANDSAT BANDS

def scale_landsat(image):
    # Scale optical surface reflectance bands
    optical = (
        image.select(["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"])
        .multiply(0.0000275)
        .add(-0.2)
    )

    # Scale thermal band to Kelvin, then convert to Celsius
    thermal_k = image.select("ST_B10").multiply(0.00341802).add(149.0)
    thermal_c = thermal_k.subtract(273.15).rename("LST_C")

    return image.addBands(optical, overwrite=True).addBands(thermal_c)


# 6. ADD INDICES

def add_indices(image):
    ndvi = image.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
    ndbi = image.normalizedDifference(["SR_B6", "SR_B5"]).rename("NDBI")
    return image.addBands([ndvi, ndbi])


# 7. GET SUMMER COLLECTION FOR A YEAR

def get_summer_collection(year, region):
    start = f"{year}-06-01"
    end = f"{year}-08-31"

    l8 = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .filterDate(start, end)
        .filterBounds(region)
    )

    l9 = (
        ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
        .filterDate(start, end)
        .filterBounds(region)
    )

    merged = l8.merge(l9)

    processed = (
        merged
        .map(mask_landsat_c2_l2)
        .map(scale_landsat)
        .map(add_indices)
    )

    return processed


# 8. CREATE ANNUAL SUMMER COMPOSITE

def make_annual_composite(year, region):
    collection = get_summer_collection(year, region)
    image_count = collection.size().getInfo()
    print(f"{year}: {image_count} summer Landsat images found.")

    if image_count == 0:
        print(f"Warning: No imagery found for {year}.")
        return None

    composite = collection.median().clip(region).set("year", year)
    return composite


# 9. SUMMARIZE BY TRACT

def summarize_by_tract(year, tracts_fc, study_area):
    image = make_annual_composite(year, study_area)

    if image is None:
        return None

    image = image.select(["LST_C", "NDVI", "NDBI"])

    stats = image.reduceRegions(
        collection=tracts_fc,
        reducer=ee.Reducer.mean(),
        scale=30
    )

    stats = stats.map(lambda f: f.set("year", year))
    return stats


# 10. EXPORT TRACT-LEVEL CSV SUMMARIES

def export_yearly_tract_stats(tracts_fc, study_area, start_year=2020, end_year=2025):
    print("Starting tract-level CSV exports...")

    for year in range(start_year, end_year + 1):
        stats_fc = summarize_by_tract(year, tracts_fc, study_area)

        if stats_fc is None:
            print(f"Skipping CSV export for {year} because no image was created.")
            continue

        task = ee.batch.Export.table.toDrive(
            collection=stats_fc,
            description=f"Lincoln_Tract_SummerStats_{year}",
            folder="GEE_Landsat_Lincoln",
            fileNamePrefix=f"lincoln_tract_summer_stats_{year}",
            fileFormat="CSV"
        )
        task.start()
        print(f"Started CSV export for {year}")


# 11. EXPORT MULTI-BAND GEOTIFFS

def export_yearly_multiband_images(study_area, start_year=2020, end_year=2025):
    print("Starting multi-band GeoTIFF exports...")

    for year in range(start_year, end_year + 1):
        image = make_annual_composite(year, study_area)

        if image is None:
            print(f"Skipping raster export for {year} because no image was created.")
            continue

        image = image.select(["LST_C", "NDVI", "NDBI"])

        task = ee.batch.Export.image.toDrive(
            image=image,
            description=f"Lincoln_Summer_Multiband_{year}",
            folder="GEE_Landsat_Lincoln",
            fileNamePrefix=f"lincoln_summer_multiband_{year}",
            region=study_area.bounds(),
            scale=30,
            maxPixels=1e13,
            fileFormat="GeoTIFF"
        )
        task.start()
        print(f"Started multi-band GeoTIFF export for {year}")


# 12. EXPORT SEPARATE GEOTIFFS FOR EACH BAND

def export_yearly_separate_band_images(study_area, start_year=2020, end_year=2025):
    print("Starting separate-band GeoTIFF exports...")

    bands = ["LST_C", "NDVI", "NDBI"]

    for year in range(start_year, end_year + 1):
        image = make_annual_composite(year, study_area)

        if image is None:
            print(f"Skipping separate band exports for {year} because no image was created.")
            continue

        for band in bands:
            task = ee.batch.Export.image.toDrive(
                image=image.select(band),
                description=f"Lincoln_{band}_{year}",
                folder="GEE_Landsat_Lincoln",
                fileNamePrefix=f"lincoln_{band.lower()}_{year}",
                region=study_area.bounds(),
                scale=30,
                maxPixels=1e13,
                fileFormat="GeoTIFF"
            )
            task.start()
            print(f"Started GeoTIFF export for {band} {year}")


# 13. MAP PREVIEW

def preview_map(year, study_area, tracts_fc):
    image = make_annual_composite(year, study_area)

    if image is None:
        print(f"No image available for map preview in {year}.")
        return None

    Map = geemap.Map(center=[40.8136, -96.7026], zoom=10)

    Map.addLayer(
        image.select("LST_C"),
        {"min": 15, "max": 45},
        f"LST {year}"
    )

    Map.addLayer(
        image.select("NDVI"),
        {"min": -0.2, "max": 0.8},
        f"NDVI {year}"
    )

    Map.addLayer(
        image.select("NDBI"),
        {"min": -0.4, "max": 0.4},
        f"NDBI {year}"
    )

    Map.addLayer(
        tracts_fc.style(**{"color": "blue", "fillColor": "00000000", "width": 1}),
        {},
        "Census Tracts"
    )

    return Map


# 14. MAIN

if __name__ == "__main__":
    initialize_earth_engine()

    gdf, tracts_fc, study_area = load_tracts()

    print("\nProject setup complete.")
    print("Available actions:")
    print("1. Preview a map")
    print("2. Export tract-level CSV summaries")
    print("3. Export multi-band GeoTIFFs")
    print("4. Export separate GeoTIFFs for each band")


    # Uncomment the lines below as needed


    # Preview one year in a notebook / interactive environment
    # map_view = preview_map(2020, study_area, tracts_fc)
    # map_view

    # Export CSV summaries for each year
    export_yearly_tract_stats(tracts_fc, study_area, start_year=2020, end_year=2025)

    # Export one multi-band GeoTIFF per year
    #export_yearly_multiband_images(study_area, start_year=2020, end_year=2025)

    # Export separate GeoTIFFs for each band and year
    export_yearly_separate_band_images(study_area, start_year=2020, end_year=2025)

    print("\nAll requested export tasks have been submitted to Google Earth Engine.")
    print("Check the Earth Engine Tasks tab or Google Drive folder for results.")