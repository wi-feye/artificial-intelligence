from requests import get, post
from dotenv import dotenv_values
from src.positioning import Positioning
import schedule
from time import sleep
import pandas as pd
from src.mapping import *
from src.prediction import *
from src.estimator import Estimator

config = dotenv_values('env_file')
WIFEYE_BASEURL_STORAGE = config['WIFEYE_BASEURL_STORAGE']
POSITIONS_CRON_SECONDS = int(config['POSITIONS_CRON_SECONDS'])
TRAINING_CRON_HOURS = int(config['TRAINING_CRON_HOURS'])
BASEDATA = WIFEYE_BASEURL_STORAGE


def position_detections():
    res = get(f'{BASEDATA}/api/details/ai/')
    buildings = res.json()
    position_detections = []
    for building in buildings:
        p = Positioning(building_raw=building)
        xy_df = p.perform_xy()
        xy_df = p.assign_area(df=xy_df)

        xy_df["id"] = xy_df.index
        result = xy_df.to_dict(orient="records")
        for detection in result:
            raw = [raw for raw in building['raws']
                   if raw['id'] == detection['id']][0]
            detection['id_building'] = raw['id_building']
            detection['timestamp'] = raw['timestamp']
        position_detections += result

    res = post(f'{BASEDATA}/api/ai/create-position-detections/',
               json=position_detections)
    print(res.json())


def training_model():
    res = get(f'{BASEDATA}/api/details/ai/positions/')
    df = pd.read_json(res)
    for i in range(len(df.index)):
        pd_df = pd.DataFrame(df["position_detections"].iloc[i])
        estimator = Estimator()
        estimator.set_train(pd_df)
        estimator.fit()
    
if __name__ == '__main__':
    schedule.every(POSITIONS_CRON_SECONDS).seconds.do(position_detections)
    schedule.every(TRAINING_CRON_HOURS).hours.do(training_model)
    while 1:
        schedule.run_pending()
        sleep(1)
