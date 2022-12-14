import json
from requests import get, post
from dotenv import dotenv_values
from src.mapping import *
from src.prediction import *
from flask import Flask, request

config = dotenv_values('env_file')
BASEDATA = config['WIFEYE_BASEURL_STORAGE']

app = Flask(__name__)

@app.route("/api/poi/<building_id>")
def find_poi(building_id):
    start_time = request.args.get("start")
    end_time = request.args.get("end")
    k = request.args.get("k")
    res = get(f'{BASEDATA}/api/position-detection/pull/{building_id}?start={start_time}&end={end_time}')
    positions = res.json()
    if len(positions) > 0:
        pred = Prediction(positions)
        poi_df = pred.poi(top=int(k) if k is not None else 5)
        return poi_df.to_dict(orient='records')
    else:
        return []


@app.route("/api/predict/<building_id>")
def predict(building_id):
    # TODO for prediction task
    date = request.args.get("date")
    return '...'