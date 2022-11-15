# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"
from positioning import *
from mapping import *
from utils import *
from parameters import *

if __name__ == "__main__":
    par = Parameter()

    df_sniffers = timeseries(_size=par.size, _from=par.start)
    devices_list = devices()
    
    rssi_df = build_data(df_sniffers, devices_list)
    rssi_col = [col for col in rssi_df.columns if col.startswith('rssi')]
    rssi_df[['x','y']] = pd.DataFrame(rssi_df[rssi_col].apply(lambda x: position(x), axis=1).tolist(), index=rssi_df.index)
    print(rssi_df)
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print(df_sniffers)

    
