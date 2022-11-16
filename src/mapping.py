import geopandas as gpd
from shapely.geometry import Polygon
from positioning import *
from parameters import Parameter
from building import Building
from folium.plugins import HeatMap
import folium
from utils import *

def geo_building():

    building = Building()

    gdf_building = gpd.GeoDataFrame(building.dictionary)
    gdf_building['geometry'] = gdf_building['geometry'].apply(lambda x : Polygon(x))

    return gdf_building

def geo_sniffers():

    par = Parameter()

    sniffers_index = []
    for i in range(len(par.sniffers_list)):
        sniffers_index.append('sniffer_'+str(i+1))

    gdf_sniffers = gpd.GeoDataFrame({'sniffer':sniffers_index})
    gdf_sniffers[["x", "y"]] = gpd.GeoDataFrame(par.sniffers_list)
    gdf_sniffers['geometry'] = gpd.points_from_xy(gdf_sniffers['x'], gdf_sniffers['y'])

    return gdf_sniffers

def geo_points(rssi_df):

    gdf_points = gpd.GeoDataFrame(rssi_df)
    gdf_points['geometry'] = gpd.points_from_xy(gdf_points['x'], gdf_points['y'])
    gdf_points['timestamp'] = gdf_points['timestamp'].astype(str)

    return gdf_points


def map(rssi_df):

    gdf_building = geo_building()
    gdf_sniffers = geo_sniffers()
    gdf_points = geo_points(rssi_df)

    map_building = gdf_building.explore(style_kwds={'color':'black','weight':3,'fillColor':'gray','fillOpacity':0.2})
    map_sniffers = gdf_sniffers.explore(m=map_building, color='red')
    map_points = gdf_points.explore(m=map_sniffers)

    return map_points.to_json()

def heatmap(rssi_df):

    gdf_building = geo_building()
    map_heat = gdf_building.explore(style_kwds={'color':'black','weight':3,'fillColor':'gray','fillOpacity':0.2})
    HeatMap(rssi_df[['y', 'x']].values).add_to(map_heat)

    return map_heat.to_json()

def heatmap_tt(rssi_df):
    gdf_building = geo_building()
    gdf_sniffers = geo_sniffers()

    map_building = gdf_building.explore(
        style_kwds={'color': 'black', 'weight': 3, 'fillColor': 'gray', 'fillOpacity': 0.2})
    map_sniffers = gdf_sniffers.explore(m=map_building, color='red')

    # List comprehension to make out list of lists
    heat_data = [[[row['x'], row['y']] for index, row in rssi_df[rssi_df['timestamp'] == i].iterrows()] for i in
                 rssi_df["timestamp"].unique()]


    # Plot it on the map
    hm = folium.plugins.HeatMapWithTime(heat_data, auto_play=True, max_opacity=0.8)
    hm.add_to(map_sniffers)

    #map_sniffers.save('/home/profeta/Scrivania/map.html')

    return map_sniffers.to_json()

def trajectories(rssi_df):

    gdf_building = geo_building()
    map_building = gdf_building.explore(style_kwds={'color':'black','weight':3,'fillColor':'gray','fillOpacity':0.2})
    gdf_points = geo_points(rssi_df)
    map_trajectories = gdf_points.explore(column='mac',m=map_building, cmap='tab20b', legend=False)

    #map_trajectories.save('/home/profeta/Scrivania/traj.html')

    return map_trajectories.to_json()

def apply_map_tt(rssi_df, mapf, freq="2H", times=5, when=None):

    if when == None:
        when = rssi_df['timestamp'].min()

    rssi_df_list = generate_time_every(rssi_df, freq, times, when)

    map_list = []
    for rssi_df in rssi_df_list:
        if not rssi_df.empty:
            map_list.append(mapf(rssi_df))

    return map_list

if __name__ == "__main__":

    rssi_df = pipeline()

    map_json = map(rssi_df)
    heatmap_json = heatmap(rssi_df)
    heatmap_through_time_json = heatmap_tt(rssi_df)
    trajectories_json = trajectories(rssi_df)
    
