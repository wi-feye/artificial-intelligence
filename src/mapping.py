import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPoint
import folium
from positioning import *
from folium.plugins import HeatMap

def geo_building(building_dict):

    for i in range(len(building_dict['space'])):
        building_dict['geometry'][i] = Polygon(building_dict['geometry'][i])

    gdf_building = gpd.GeoDataFrame(building_dict)

    return gdf_building

def geo_sniffers():

    sniffers_index = []
    for i in range(len(sniffers_list)):
        sniffers_index.append('sniffer_'+str(i+1))

    gdf_sniffers = gpd.GeoDataFrame({'sniffer':sniffers_index})
    gdf_sniffers[["x", "y"]] = gpd.GeoDataFrame(sniffers_list)
    gdf_sniffers['geometry'] = gpd.points_from_xy(gdf_sniffers['x'], gdf_sniffers['y'])

    return gdf_sniffers

def geo_points(rssi_df):

    gdf_points = gpd.GeoDataFrame(rssi_df)
    gdf_points['geometry'] = gpd.points_from_xy(gdf_points['x'], gdf_points['y'])
    gdf_points['timestamp'] = gdf_points['timestamp'].astype(str)

    return gdf_points

def spatial_join(building_dict, rssi_df):

    gdf_building = geo_building(building_dict)
    gdf_points = geo_points(rssi_df)

    return gpd.sjoin(gdf_points, gdf_building)


def map(building_dict, rssi_df):

    gdf_building = geo_building(building_dict)
    gdf_sniffers = geo_sniffers()
    gdf_points = geo_points(rssi_df)

    map_building = gdf_building.explore(style_kwds={'color':'black','weight':3,'fillColor':'gray','fillOpacity':0.2})
    map_sniffers = gdf_sniffers.explore(m=map_building, color='red')
    map_points = gdf_points.explore(m=map_sniffers)

    return map_points
    # return map_points.to_json()

def heatmap(building_dict, rssi_df):

    gdf_building = geo_building(building_dict)
    map_heat = gdf_building.explore(style_kwds={'color':'black','weight':3,'fillColor':'gray','fillOpacity':0.2})
    HeatMap(rssi_df[['y', 'x']].values).add_to(map_heat)

    return map_heat.to_json()

def trajectories(building_dict, rssi_df):

    gdf_building = geo_building(building_dict)
    map_building = gdf_building.explore(style_kwds={'color':'black','weight':3,'fillColor':'gray','fillOpacity':0.2})
    gdf_points = gpd.GeoDataFrame(rssi_df)
    map_trajectories = gdf_points.explore(column='mac',m=map_building, cmap='tab20b', legend=False)

    return map_trajectories.to_json()

if __name__ == "__main__":

    rssi_df = pipeline()

    # list of vertices' positions for each room in meters ((0,0) is the point of reference)
    building_dict = {'space':['X3', 'X2'], 'geometry':[[(-1,-0.5),(5,-0.5),(5,8.3),(-1,8.3)],[(5,-0.5),(9.8,-0.5),(9.8,8.3),(5,8.3)]]}

    map_json = map(building_dict, rssi_df)
    heatmap_json = heatmap(building_dict, rssi_df)
    trajectories_json = trajectories(building_dict, rssi_df)