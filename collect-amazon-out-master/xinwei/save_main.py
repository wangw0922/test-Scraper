# -*- coding: utf-8 -*-
# @Time    : 2023/1/17 15:55
# @Author  : 李文霖
import sys
sys.path.append('../')
import os
import multiprocessing
import re
from xinwei.project.RedisSaveToMongoDb.src.redis_save_mongo import RedisSaveToMongo
from xinwei.project.setting import process_num
from xinwei.project.Collect.src.loggerDefine import logger_define

logging = logger_define(os.getcwd(), 'save_main')


def save_main():
    with open("project/setting.py", "r", encoding="utf-8") as f:
        txt = f.read()
    result = re.search("redis_db\s=\s(\d)", txt).group(1)
    pool = multiprocessing.Pool(process_num)
    if result == '1':
        logging.info("---------------------------PRODUCE ENVIRONMENT---------------------------------------")
    else:
        logging.info('----------------------------TEST ENVIRONMENT-----------------------------------------')
    logging.info(f"process number：{process_num}")
    for i in range(process_num):
        pool.apply_async(RedisSaveToMongo.run_save)
    pool.close()
    pool.join()


if __name__ == '__main__':
    save_main()
