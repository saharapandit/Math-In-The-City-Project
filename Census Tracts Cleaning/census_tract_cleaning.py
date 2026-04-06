import geopandas as gpd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'Data'

def load_tracts():
    return gpd.read_file(DATA_DIR / 'Census_Tracts_2020.geojson')

def clean_tracts(tracts):
    # Projection to WGS84 so lon/lat boundaries can be visualized consistently.
    cleaned_tracts = tracts.to_crs(epsg=4326)

    # Removing unnecessary fields while keeping tract id and geometry.
    final_tracts = cleaned_tracts[['GEOID', 'geometry']].copy()

    if not final_tracts.is_valid.all():
        print("Invalid geometries found. Attempting to fix...")
        final_tracts['geometry'] = final_tracts.geometry.make_valid()

    return final_tracts


def export_tracts(final_tracts):
    final_tracts.to_file(DATA_DIR / 'cleanedCensusTracts.geojson', driver='GeoJSON')


def main():
    tracts = load_tracts()
    final_tracts = clean_tracts(tracts)
    export_tracts(final_tracts)

    print('Complete')
    print("Column Count:", len(final_tracts.columns))


if __name__ == '__main__':
    main()
