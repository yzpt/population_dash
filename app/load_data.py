import geopandas as gpd
from datetime import datetime

def load_data(
    precison: str = '1000m',
) -> gpd.GeoDataFrame:
    f = 'f'
    print(f'{datetime.now()}: Loading data from communes_with_population_{precison}_{f}.gpkg')
    gdf = gpd.read_file(f'communes_with_population_{precison}_{f}.gpkg')
    print(f'Data loaded: {len(gdf)} rows')
    return gdf
