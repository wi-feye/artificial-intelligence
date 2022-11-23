from requests import get, post
from dotenv import dotenv_values
from final_class import Positioning
import schedule
from time import sleep

config = dotenv_values('env_file')
WIFEYE_BASEURL_STORAGE = config['WIFEYE_BASEURL_STORAGE']
CRON_SECONDS = int(config['CRON_SECONDS'])

def main():
    res = get(f'{WIFEYE_BASEURL_STORAGE}/buildings')
    buildings = res.json()
    position_detections = []
    for building in buildings:
        p = Positioning(building['raws'], building['sniffers'], building['areas'])
        result = p.perform_xy()
        result = p.assign_area(df=result) 
        result  = p.return_json(result)
        position_detections += result
    res = post(f'{WIFEYE_BASEURL_STORAGE}/create-position-detections', json=position_detections)
    print(res.status_code)


if __name__ == '__main__':
    schedule.every(CRON_SECONDS).seconds.do(main)
    while 1:
        schedule.run_pending()
        sleep(1)