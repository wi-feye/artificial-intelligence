from requests import get, post
from dotenv import dotenv_values
from final_class import Positioning
import schedule
from time import sleep

config = dotenv_values('env_file')
WIFEYE_BASEURL_STORAGE = config['WIFEYE_BASEURL_STORAGE']
CRON_SECONDS = int(config['CRON_SECONDS'])

def main():
    # BASEDATA = WIFEYE_BASEURL_STORAGE
    # res = get(f'{BASEDATA}/api/details/ai/')
    # buildings = res.json()
    import json
    with open('./raw_data.json', 'r') as file:
        buildings = json.load(file)
    position_detections = []
    for building in buildings:
        p = Positioning(building['raws'], building['sniffers'], building['areas'])
        result = p.perform_xy()
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