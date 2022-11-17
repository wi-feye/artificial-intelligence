# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"
from positioning import *
from mapping import *
from analysis import *
from utils import *
from parameters import *

if __name__ == "__main__":
    
    # Positioning
    rssi_df = pipeline()
    print(rssi_df)
    
    # Mapping
    map_json = map(rssi_df)
    heatmap_json = heatmap(rssi_df)
    heatmap_through_time_json = heatmap_tt(rssi_df)
    trajectories_json = trajectories(rssi_df)
    
    # Analysis
    gdf_points_final = enrich_points(rssi_df)
    gdf_building_final = enrich_spaces(rssi_df)