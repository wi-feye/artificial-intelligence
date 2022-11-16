import datetime
import pandas as pd 

class TimeException(Exception):
    pass

    """do analyse on the interval between start and end
    """
def time_interval(df, start=None, end=None, time_col="timestamp"):
    if start == None and end == None:
        raise TimeException("please define an interval of starting or ending")
    if  start > end:
        raise TimeException("start and end not properly defined")
    
    mask= pd.Series(True, index=df.index)
    if start != None: 
        df_start = pd.to_datetime(df[time_col]) > start 
        mask = mask & df_start
    if end != None:
        df_end = pd.to_datetime(df[time_col]) < end
        mask = mask & df_end

    return df.loc[mask]

    """show the activeness index in a given period of time, from start to stop
    """
def activeness_index(df, start=None, stop=None):
    interested_df = time_interval(df, start, stop)
    print(len(interested_df.index))
    
    """
    generate dataframes every freq for "times" times starting from "when"
    
    freq: use the combination of number + alias
    possible alias are:
    - W weekly
    - M monthly
    - D daily
    - Y yearly
    - H hourly
    - T or min minutly
    - S secondly
    more details: https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases
    
    times: how many times generate the time
    when: if not defined it will generate time from 1H before
    """
def generate_time_every(df, freq="2H", times=5, when=None):
    if when == None:
        when = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    
    df_intervals = []
    ids = pd.date_range(when, periods=times, freq=freq)
    for i in range(len(ids)-1):
        df_intervals.append(time_interval(df, ids[i].strftime("%Y-%m-%d %H:%M:%S"),
                                            ids[i+1].strftime("%Y-%m-%d %H:%M:%S")))
    
    return df_intervals