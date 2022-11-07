def devices(URL_DEVICES, headers):
    req = requests.get(URL_DEVICES, headers=headers)
    return req.json()['devices']


def retrieve_probs_zerynth(URL_TIMESERIES,_size=500, _from=1):
    req = requests.get(f'{URL_TIMESERIES}?from={_from}&size={_size}', headers=headers)
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
    df_sniffer['timestamp'] = pd.to_datetime(df_sniffer['timestamp'], format="%Y-%m-%d %H:%M:%S").apply(lambda x: x.replace(microsecond=0))
    subset =['timestamp', 'mac']
    df_sniffer = df_sniffer[['timestamp','mac','rssi']].groupby(as_index=False,by=subset).median()
    df_sniffer = df_sniffer.rename(columns={'rssi':'rssi_'+str(i)})
    
    return df_sniffer


def build_data(df_sniffers, devices_list):
    
    df_sniffer_start = df_sniffers[df_sniffers['device_id'] == devices_list[0]['id']]
    df_sniffer_start = process_data(df_sniffer_start, 1)
    
    for i in range(len(devices_list)-1):
        
        df_sniffer_new = df_sniffers[df_sniffers['device_id'] == devices_list[i+1]['id']]
        df_sniffer_new = process_data(df_sniffer_new, i+2)
        df_sniffer_start = df_sniffer_start.merge(df_sniffer_new, how="inner", on=["timestamp", "mac"])

    rssi_df = df_sniffer_start
    
    return rssi_df


def position(rss_list, sniffer_list):

    # 1 meter rss
    rss0 = -50

    # environment constant in range [2,4] 2 pochi ostacoli, 4 molti ostacoli
    n = 3.2

    P = np.array(sniffer_list)
    temp_A = P[-1] - P
    temp_A = temp_A[0:-1] 
    A = 2 * temp_A

    # from rssi to distance in meters
    rss_to_dist = lambda rss, n: np.power(10, (rss0 -rss) / (10 * n)) 

    d = np.empty((0,1))
    for rss in rss_list:
        d = np.append(d, [[rss_to_dist(rss, n)]], axis=0)

    d_2 = np.power(d,2)
    temp_d = d_2 - d_2[-1]
    temp_d = temp_d[0:-1]

    P_2 = np.power(P,2)
    temp_b1 = P_2[-1] - P_2
    temp_b1 = temp_b1[0:-1]

    b = np.einsum('ij->i', temp_b1).reshape(temp_d.shape) + temp_d

    X = np.dot(np.linalg.pinv(A), b)

    return X[0][0], X[1][0]


def pipeline(URL_DEVICES, URL_TIMESERIES, headers):
    
    df_sniffers = retrieve_probs_zerynth(URL_TIMESERIES)
    devices_list = devices(URL_DEVICES, headers)
    
    rssi_df = build_data(df_sniffers, devices_list)
    
    # sniffers' positions in meters ((0,0) is the point of reference)
    # WARNING!: take care of the sniffers' ordering
    sniffer_list = [(9.6, 0), (0, 0), (3.2, 3.4)]

    rssi_col = [col for col in rssi_df.columns if col.startswith('rssi')]
    rssi_df[['x','y']] = pd.DataFrame(rssi_df[rssi_col].apply(lambda x: position(x, sniffer_list), axis=1).tolist(), index=rssi_df.index)
    
    return rssi_df

if __name__ == "__main__":
	WORKSPACE = 'wks-7e2yv6y5ijmc'
	URL_DEVICES = f'https://api.zdm.zerynth.com/v3/workspaces/{WORKSPACE}/devices'
	URL_TIMESERIES = f'https://api.storage.zerynth.com/v3/timeseries/{WORKSPACE}/data'
	API_KEY = 'G9froN8D4R.cF1znVzGvCejjc5BrzCsSqcqMaANPgRmFXMglCAWhkYttQFTymThnrf1ta7OQVP4'

	headers = {'X-API-KEY': API_KEY}

	rssi_df = pipeline(URL_DEVICES, URL_TIMESERIES, headers)
	

