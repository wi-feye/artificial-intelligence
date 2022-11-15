import pandas as pd
import numpy as np
import requests
from parameters import *

# list zerynth workspaces (default: atzeni workspace, Smart Application project: our workspace)
def workspaces():
    req = requests.get(f'https://api.zdm.zerynth.com/v3/workspaces', headers=HEADERS)
    return req.json()['workspaces']


# list of devices of selected workspace
def devices(workspace_id=WORKSPACE):

    req = requests.get(f'https://api.zdm.zerynth.com/v3/workspaces/{workspace_id}/devices', headers=HEADERS)
    return req.json()['devices']


# list timeseries of all devices related to a workspace
def timeseries(workspace_id=WORKSPACE, _size=500, _from=1):

    req = requests.get(f'https://api.storage.zerynth.com/v3/timeseries/{workspace_id}/data?from={_from}&size={_size}', headers=HEADERS)
    res = req.json()['result']

    data = {
        'device_id': [], 
        'timestamp': [], 
        'mac': [], 
        'rssi': []
    }
    for fp in res:
        for scan in fp['payload']['scans']:
            data['device_id'].append(fp['device_id'])
            data['timestamp'].append(fp['timestamp_device'])
            data['mac'].append(scan[3])
            data['rssi'].append(scan[4])

    return pd.DataFrame.from_dict(data)


def process_data(df_sniffer, i):
    
    df_sniffer.reset_index(inplace=True)
    df_sniffer = df_sniffer[['timestamp', 'mac', 'rssi']]

    df_sniffer['timestamp'] = pd.to_datetime(df_sniffer['timestamp'], format="%Y-%m-%d %H:%M:%S").apply(lambda x: x.replace(second=0,microsecond=0))
    subset =['timestamp', 'mac']
    df_sniffer = df_sniffer[['timestamp','mac','rssi']].groupby(as_index=False,by=subset).median()

    df_sniffer = df_sniffer.rename(columns={'rssi':'rssi_'+str(i)})
    
    return df_sniffer


def build_data(df_sniffers, devices_list):

    not_empty_sniffers = []
    for i in range(len(devices_list)):
        df_sniffer = df_sniffers[df_sniffers['device_id'] == devices_list[i]['id']]
        if not df_sniffer.empty:
            not_empty_sniffers.append(i)

    df_sniffer_start = df_sniffers[df_sniffers['device_id'] == devices_list[not_empty_sniffers[0]]['id']]
    df_sniffer_start = process_data(df_sniffer_start, not_empty_sniffers[0] + 1)

    for i in not_empty_sniffers[1:]:

        df_sniffer_new = df_sniffers[df_sniffers['device_id'] == devices_list[i]['id']]
        df_sniffer_new = process_data(df_sniffer_new, i+1)
        df_sniffer_start = df_sniffer_start.merge(df_sniffer_new, how="inner", on=["timestamp", "mac"])

    rssi_df = df_sniffer_start
    if rssi_df.empty:
        raise Exception("Data collected by sniffers are not mergeable: the timestamps of different sniffers do not intersect")
    
    return rssi_df


def position(rss_list):

    par = Parameter()

    if len(rss_list) >= 3:
        P = np.array(par.sniffers_list)
        temp_A = P[-1] - P
        temp_A = temp_A[0:-1] 
        A = 2 * temp_A

        # from rssi to distance in meters
        rss_to_dist = lambda rss, n_env: np.power(10, (par.rss0 -rss) / (10 * n_env)) 

        d = np.empty((0,1))
        for rss in rss_list:
            d = np.append(d, [[rss_to_dist(rss, par.n_env)]], axis=0)

        d_2 = np.power(d,2)
        temp_d = d_2 - d_2[-1]
        temp_d = temp_d[0:-1]

        P_2 = np.power(P,2)
        temp_b1 = P_2[-1] - P_2
        temp_b1 = temp_b1[0:-1]

        b = np.einsum('ij->i', temp_b1).reshape(temp_d.shape) + temp_d

        X = np.dot(np.linalg.pinv(A), b)

        x = X[0][0]
        y = X[1][0]
    else:
        sniffer_index_max = np.argmax(rss_list)
        x = par.sniffers_list[sniffer_index_max][0]
        y = par.sniffers_list[sniffer_index_max][1]

    return x, y


def pipeline():

    par = Parameter()

    df_sniffers = timeseries(_size=par.size, _from=par.start)
    devices_list = devices()
    
    rssi_df = build_data(df_sniffers, devices_list)
    rssi_col = [col for col in rssi_df.columns if col.startswith('rssi')]
    rssi_df[['x','y']] = pd.DataFrame(rssi_df[rssi_col].apply(lambda x: position(x), axis=1).tolist(), index=rssi_df.index)
    
    return rssi_df

    
if __name__ == "__main__":

    rssi_df = pipeline()