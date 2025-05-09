import sys
sys.path.append('....')
import datetime
import os
import pickle
import time
import traceback
import requests
from redis.client import StrictRedis
from sympy.core import function
from xinwei.project.Collect.src.edition import edition
from xinwei.project.Collect.src.loggerDefine import logger_define
from xinwei.project.setting import redis_host, redis_port, redis_password, redis_data_db, redis_data_collection, get_token_url, tunnel_name, post_edition_url


logging = logger_define(os.getcwd(), 'Functions')


def retry(func) -> function:
    """
    The decorator use to retry
    """
    def wrapper():
        while True:
            try:
                func()
                break
            except:
                logging.error(traceback.format_exc())
                time.sleep(3)
                continue
    return wrapper


def request_allow() -> None:
    """
    Get token of request
    """
    while True:
        try:
            token_res = requests.post(url=get_token_url, data={"tunnel_name": tunnel_name})
            token_dict = token_res.json()
            token = token_dict.get("token")
            result = token_dict.get("result")
        except:
            logging.error(traceback.format_exc())
            time.sleep(3)
            continue
        if result:
            logging.info(f'-------------Current token: {token}----------------')
            return None
        else:
            logging.error('Request is overclocking,please waiting')
            time.sleep(61 - datetime.datetime.now().second)


def get_tort_data(tortType) -> pickle:
    """
    Get data of tort
    """
    return []
    # logging.info(f"Geting {tortType}")
    # while True:
    #     try:
    #         server = StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=5)
    #         tort_data = server.get(tortType)
    #         break
    #     except:
    #         logging.error(traceback.format_exc())
    # logging.info("Successful!!")
    # return pickle.loads(tort_data)


def push_data(_data) -> None:
    """
    Save data to redis database
    """
    server = StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=redis_data_db)
    pickle_data = pickle.dumps(_data)
    server.lpush(redis_data_collection, pickle_data)


def get_edition() -> dict:
    """
    Determine current editon whether it is latest
    """
    while True:
        try:
            data = {"edition": edition}
            response = requests.post(post_edition_url, data=data).json()
            if response.get("pass"):
                logging.info('Edition verification successful!!')
                return response
            else:
                logging.info('Current Edition is unavailable,please update Edition to latest')
                time.sleep(5)
                continue
        except:
            logging.error(traceback.format_exc())
            logging.error('Request of Edition verification exception')
            time.sleep(5)
            continue


if __name__ == '__main__':
    a = get_edition()
    print(a)
