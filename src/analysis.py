from positioning import *
from mapping import *

def enrich_points(rssi_df):

    gdf_building = geo_building()
    gdf_points = geo_points(rssi_df)
    gdf_points = gdf_points.sjoin(gdf_building)
    gdf_points.drop(['index_right'], axis=1, inplace=True)
    
    return gdf_points

def enrich_spaces(rssi_df):

    gdf_points_enriched = enrich_points(rssi_df)

    gdf_building = geo_building()
    print(gdf_building)
    gdf_building = gdf_building.set_index('space').join(gdf_points_enriched['space'].value_counts())
    gdf_building.fillna(0, inplace=True)
    print(gdf_building)
    gdf_building.rename(columns={"space": "count"}, inplace=True)
    print(gdf_building)
    gdf_building.reset_index(inplace=True)
    print(gdf_building)

    gdf_building['count_pct'] = gdf_building['count'] / gdf_building['count'].sum()
    gdf_building['area'] = gdf_building['geometry'].area
    gdf_building['density'] = gdf_building['count'] / gdf_building['area']

    return gdf_building

if __name__ == "__main__":
    rssi_df = pipeline()

    gdf_points_final = enrich_points(rssi_df)
    gdf_building_final = enrich_spaces(rssi_df)
