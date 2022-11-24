import datetime
import pandas as pd 

class TimeException(Exception):
    pass

def time_interval(df, start=None, end=None, time_col="timestamp"):
    """
        do analyse on the interval between start and end
    Args:
        df (DataFrame): pandas DataFrame
        start (datetime | str, optional): start time. Datetime format or a string that follows a proper date format (e.g. YYYY-MM-DD HH:MM:SS). Defaults to None.
        end (datetime | str, optional): end time. Datetime format or a string that follows a proper date format (e.g. YYYY-MM-DD HH:MM:SS). Defaults to None.
        time_col (str, optional): the timestamp columns name. Defaults to "timestamp".

    Raises:
        TimeException: no time interval defined
        TimeException: start time > end time

    Returns:
        DataFrame: the portion of the dataframe delimited by [start : end]
    """
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


def activeness_index(df, start=None, stop=None):
    """
    # todo
    show the activeness index in a given period of time, from start to stop
    """
    interested_df = time_interval(df, start, stop)
    tot = len(interested_df.index)
    return tot
    

def generate_time_every(df, freq="2H", times=5, when=None):
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
    
    Args:
        times: how many times generate the time
        when: if not defined it will generate time from 1H before
        
    Return:
        list: a list of dataframe splitted into chunks w.r.t. freq
    """
    if when == None:
        when = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    
    df_intervals = []
    ids = pd.date_range(when, periods=times, freq=freq)
    for i in range(len(ids)-1):
        df_intervals.append(time_interval(df, ids[i].strftime("%Y-%m-%d %H:%M:%S"),
                                            ids[i+1].strftime("%Y-%m-%d %H:%M:%S")))
    
    return df_intervals


def split_dataframe_with_dim(df, n=100):
    """
    splits the dataframe into little chunks of n rows

    Args:
        df (DataFrame): pandas DataFrame
        n (int, optional): dimension of each chunk. Defaults to 100.
        
    Return:
        list: a list of DataFrame each with n row
    """
    df_list = []
    left = 0
    for right in range(n ,len(df.index), n):
        df_list.append(df.iloc[left:right, :])
        left = right
    return df_list

def send_to_DB(df, chunk_size=1000):
    """
    util function to sends a DataFrame to the DB

    Args:
        df (DataFrame): pandas DataFrame
        chunk_size (int, optional): the size of each chunks thr divided DataFrame. Defaults to 1000.
    """
    chunks = split_dataframe_with_dim(df, chunk_size)
    
    for chunk in chunks:
        json_form = chunk.to_json()
        # todo
        # ask the API to send to DB

def convert_json_to_df(json_file):
    pd.read_json(json_file)