import pandas as pd
import json
from src.estimator import *
from requests import get, post
from dotenv import dotenv_values
from src.mapping import *
from src.prediction import *
from flask import Flask, request
from datetime import datetime, timedelta
import math

config = dotenv_values('env_file')
BASEDATA = config['WIFEYE_BASEURL_STORAGE']

app = Flask(__name__)


@app.route("/api/poi/<building_id>")
def find_poi(building_id):
    start_time = request.args.get("start")
    end_time = request.args.get("end")
    k = request.args.get("k")
    res = get(
        f'{BASEDATA}/api/position-detection/pull/{building_id}?start={start_time}&end={end_time}')
    positions = res.json()
    if len(positions) > 0:
        pred = Prediction(positions)
        poi_df = pred.poi(top=(int(k)) if k is not None and int(k) > 1 else 5)
        poi_list = poi_df.to_dict(orient='records')
        for poi in poi_list:
            poi['likelihood'] = math.exp(poi['likelihood'])
        max_l = poi_list[0]['likelihood']
        for poi in poi_list:
            poi['likelihood'] = round((poi['likelihood'] / max_l), 4)
        return poi_list
    else:
        return []


@app.route("/api/predict/<building_id>")
def predict(building_id):
    target_date = request.args.get("date").replace("Z", "")
    target_date = datetime.fromisoformat(target_date)
    max_date = get(
        f'{BASEDATA}/api/position-detection/maxdate/{building_id}').json()["maxDate"]
    max_date = datetime.fromisoformat(max_date)
    min_date = max_date - timedelta(minutes=10)
    res = get(
        f'{BASEDATA}/api/details/ai/positions/{building_id}?start={min_date.isoformat()}&end={max_date.isoformat()}').json()
    # maximum future_steps are 3 days
    delta_time = min(
        int((target_date - max_date).total_seconds() // 600), 6 * 24 * 3)

    estimator = Estimator()
    estimator.load_model()
    prediction = estimator.predict([res], future_steps=delta_time)

    return prediction
