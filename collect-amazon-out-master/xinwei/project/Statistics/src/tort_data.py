import pickle
import sys
import time
import traceback
import requests
from redis.client import StrictRedis
import datetime
from src.setting import redis_host, redis_port, redis_password
import logging
import coloredlogs
sys.path.append('../')

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s:%(message)s')
coloredlogs.install(level='INFO')


def get_tort(name: str, url: str) -> dict:
    """
    Get word of Tort information

    Return a dict that contain keyword of Tort
    """
    while True:
        try:
            logging.info(f'Getting {name}')
            tort_data = requests.get(url).json()['data']
            if tort_data:
                break
        except:
            logging.info(f'Getting {name} word of Tort failed')
    torts = {}
    if isinstance(tort_data, list):
        for data in tort_data:
            if data.get('value'):
                torts[data.get('value')] = data.get('Collect')
            else:
                logging.info(f'Keyword of Tort is empty')
                continue
        if torts:
            return torts
        else:
            logging.info(f'Finally update information of Tort of headline failed, data is empty')
            return torts
    else:
        logging.info(f'Finally update information of Tort of headline failed, it is not iterable')
        return torts


def update_tort() -> None:
    """
    Update information of Tort regular
    """
    while True:
        now_time = datetime.datetime.now()
        logging.info(f"Waiting.....")
        if now_time.minute in (30, 0):
            while True:
                try:
                    logging.info("Start update data of Tort")
                    server = StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=5)
                    brand_tort = get_tort(name='brand', url='http://erp.xinweitech.com/api/tort/findList/1')
                    pickle_data = pickle.dumps(brand_tort)
                    server.set('brand_tort', pickle_data)
                    title_tort = get_tort(name='title', url='http://erp.xinweitech.com/api/tort/findList/2')
                    pickle_data = pickle.dumps(title_tort)
                    server.set('title_tort', pickle_data)
                    keyword_tort = get_tort(name='keyword', url='http://erp.xinweitech.com/api/tort/findList/4')
                    pickle_data = pickle.dumps(keyword_tort)
                    server.set('keyword_tort', pickle_data)
                    classic_tort = get_tort(name='category', url='http://erp.xinweitech.com/api/tort/findList/5')
                    pickle_data = pickle.dumps(classic_tort)
                    server.set('classic_tort', pickle_data)
                    logging.info("update successful！！")
                    break
                except:
                    logging.info("update failed！！")
                    logging.info(traceback.format_exc())
                    continue
            time.sleep(60-now_time.second)
        else:
            time.sleep(60-now_time.second)


if __name__ == '__main__':
    update_tort()
