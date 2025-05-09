# coding=gbk
import sys
sys.path.append('../')
from redis.client import StrictRedis
import os
import multiprocessing
import traceback
import random
from xinwei.project.Control.app.api.whether_quit import Quit
from xinwei.project.Collect.src.loggerDefine import logger_define
from xinwei.project.Collect.src.spider import run, get_data_list
from xinwei.project.Collect.src.dd import ddmessage
from xinwei.project.setting import process_num, coroutine_num, mysql_host, machine_mark_code, redis_host, redis_port, \
    redis_password, redis_db

logging = logger_define(os.getcwd(), 'run_spider')


def run_crawl() -> None:
    """
    Running collect
    """
    with open("project/Collect/src/banner.txt", "r", encoding="utf8") as f:
        print(f.read())
    logging.info("--------------------------Running collect------------------------------------")
    result, message = Quit().start(machine_code=machine_mark_code)
    if not result:
        logging.error(message)
        sys.exit()
    crawl_process_number = os.getpid()
    redis_service = StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=redis_db)
    redis_service.set("crawl_process_number", crawl_process_number)
    logging.info("Getting user id of all store manager")
    # 获取全部任务信息
    task_list = get_data_list()
    data_list = list()
    # 优先只采集店长本店任务
    if len(machine_mark_code) == 2:
        for i in range(process_num):
            machine_code = f'{machine_mark_code}-{i}'
            data_list.append({'userId': int(machine_mark_code), 'machineMark': machine_code})
    # 根据进程数量补充任务
    while len(data_list) < process_num and len(data_list) < len(task_list):
        data_one = random.choice(task_list)
        if data_one not in data_list:
            data_list.append(data_one)
    logging.info(f'data_list >>>>>>>>>>>> {data_list}')
    logging.info(f'machine code >>>>>>>>>>>> {machine_mark_code}')
    logging.info(f'number of process >>>>>>>>>>>> {len(data_list)}')
    logging.info(f"number of coroutine concurrentcy >>>>>>>>>>>> {coroutine_num}")
    if mysql_host == '198.11.173.2':
        logging.info("---------------------------PRODUCE ENVIRONMENT---------------------------------------")
    else:
        logging.info('----------------------------TESE ENVIRONMENT-----------------------------------------')
    # 开启进程
    try:
        pool = multiprocessing.Pool(process_num)
        pool.map(run, data_list)
        pool.close()
        pool.join()
    except ZeroDivisionError:
        logging.info("--------------------------EXIT--------------------------")
        sys.exit()
    except Exception:
        logging.error(traceback.format_exc())
        ddmessage(traceback.format_exc())
        pass


if __name__ == '__main__':
    run_crawl()
