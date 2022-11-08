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
    