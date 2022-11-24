# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"
# from positioning import *
# from mapping import *
# from analysis import *
# from utils import *
# from parameters import *
# from prediction import *
# import pandas as pd


import json
from requests import get, post
from dotenv import dotenv_values
from collecting import Collecting
import schedule
from time import sleep

config = dotenv_values('env_file')
WIFEYE_BASEURL_STORAGE = config['WIFEYE_BASEURL_STORAGE']
CRON_SECONDS = int(config['CRON_SECONDS'])

config = dotenv_values('env_file')
WIFEYE_BASEURL_STORAGE = config['WIFEYE_BASEURL_STORAGE']
CRON_SECONDS = int(config['CRON_SECONDS'])

def main():
    # BASEDATA = WIFEYE_BASEURL_STORAGE
    # res = get(f'{BASEDATA}/api/details/ai/')
    with open("./raw_data.json", "r") as file:
        res = json.load(file)
        
    buildings = res
    position_detections = []
    for building in buildings:
        p = Collecting(building['raws'], building['sniffers'], building['areas'])
        result = p.collect()
        result = p.assign_area(df=result) 
        result  = p.return_json(result)
        for detection in result:
            raw = [raw for raw in building['raws'] if raw['id'] == detection['id']][0]
            detection['id_building'] = raw['id_building']
            detection['timestamp'] = raw['timestamp']
        position_detections += result
    # res = post(f'{BASEDATA}/api/ai/create-position-detections/', json=position_detections)
    # print(res.json())
    print(position_detections)


if __name__ == '__main__':
    main()
    # schedule.every(CRON_SECONDS).seconds.do(main)
    # while 1:
    #     schedule.run_pending()
    #     sleep(1)

# def main():
#     BASEDATA = WIFEYE_BASEURL_STORAGE
#     res = get(f'{BASEDATA}/api/details/ai/')
#     buildings = res.json()
#     for building in buildings:
#         p = Collecting(building['raws'], building['sniffers'], building['areas'])
#         xy_df = p.collect()
#         print(xy_df)


# if __name__ == '__main__':
#     schedule.every(CRON_SECONDS).seconds.do(main)
#     while 1:
#         schedule.run_pending()
#         sleep(1)


# if __name__ == "__main__":
    
#     # Positioning
#     rssi_df = pipeline()
#     print(rssi_df)

#     # Points of interest
#     # rssi_df, kde = all_is_likelihood(rssi_df)
#     # poi = points_of_interest(rssi_df, kde)
#     # print(poi)

#     # Sampling
#     # sample = sample(kde,100)
#     # print(sample)
#     # sample_df = pd.DataFrame(sample, columns=['x','y'])
#     # print(sample_df)
    
#     # Mapping
#     # map_json = map(rssi_df)
#     # heatmap_json = heatmap(rssi_df)
#     # heatmap_through_time_json = heatmap_tt(rssi_df)
#     # trajectories_json = trajectories(rssi_df)
    
#     # Analysis
#     # gdf_points_final = enrich_points(rssi_df)
#     # gdf_building_final = enrich_spaces(rssi_df)