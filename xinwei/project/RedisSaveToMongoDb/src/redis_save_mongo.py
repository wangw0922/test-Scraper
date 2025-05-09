import asyncio
import datetime
import multiprocessing
import os
import pickle
import random
import time
import traceback
from redis.client import StrictRedis
from xinwei.project.Collect.src.dd import ddmessage
from xinwei.project.Collect.src.update_task import UpdateTask
from xinwei.project.RedisSaveToMongoDb.src.async_save_data import AsyncMongoData
from xinwei.project.setting import redis_host, redis_port, redis_password, redis_data_db, process_num, redis_data_collection, machine_mark_code
from xinwei.project.Collect.src.loggerDefine import logger_define

logging = logger_define(os.getcwd(), 'redis_save_mongo')
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class RedisSaveToMongo(object):

    def __init__(self, taskId=None, page=None, total_page=None, sys_expect_quantity=None, data_list=None, types=None):
        self.taskId = taskId
        self.page = page
        self.total_page = total_page
        self.sys_expect_quantity = sys_expect_quantity
        self.data_list = data_list
        self.type = types

    @staticmethod
    async def save(data) -> None:
        """Save data to mongodb"""
        await AsyncMongoData(data_list=data).run()

    def main(self) -> None:
        """Run event loop"""
        # 创建一个集合用于存储已经出现过的asin
        seen_asins = set()

        # 创建一个新的双列表用于存储去重后的数据
        filtered_double_list = []

        # 遍历原始的双列表
        for sublist in self.data_list:
            # 创建一个新的子列表用于存储去重后的项目
            new_sublist = []
            for item in sublist:
                # 提取当前项目的asin
                asin = item['profile']['asin']
                # 检查asin是否已经出现过
                if asin not in seen_asins:
                    # 如果没有出现过，添加到新的子列表和集合中
                    new_sublist.append(item)
                    seen_asins.add(asin)
            # 将去重后的子列表添加到新的双列表中
            if new_sublist:
                filtered_double_list.append(new_sublist)
        self.data_list = filtered_double_list

        if self.data_list:
            loop = asyncio.get_event_loop()
            tasks = [asyncio.ensure_future(self.save(data)) for data in self.data_list]
            loop.run_until_complete(asyncio.wait(tasks))
            while True:
                try:
                    # UpdateTask(taskId=self.taskId, page=self.page, total_page=self.total_page, sys_expect_quantity=self.sys_expect_quantity).update_task()
                    break
                except:
                    logging.error(f"Update task data error, retry:{traceback.format_exc()}--{self.taskId}")
                    continue
            logging.info(f"updata task data->{self.taskId}")
            if self.page == self.total_page:
                logging.info(f"Task end->{self.taskId}")
        else:
            logging.info("Task is empty!")


    @staticmethod
    def pop_data() -> dict:
        """
        Get data from redis

        Return detail data of product
        """
        while True:
            try:
                server = StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=redis_data_db)
                length = server.llen(redis_data_collection)
                logging.info(f"{datetime.datetime.now()}-machine:{machine_mark_code}-redis_data_db:{redis_data_db}->left data count:<{length}>")
                if length:
                    pickle_data = server.rpop(redis_data_collection)
                    try:
                        data = pickle.loads(pickle_data)
                    except TypeError:
                        logging.error("Queue is empty,failed request of data!")
                        continue
                    if data:
                        logging.info(f"pop->machine:{machine_mark_code}--taskId:{data.get('taskId')}--page:{data.get('page')}")
                        return data
                else:
                    return {}
            except:
                logging.error(f"Internet connect error!\n{traceback.format_exc()}")

    @staticmethod
    def run_save() -> None:
        """Method to running"""
        try:
            while True:
                data = RedisSaveToMongo.pop_data()
                if data:
                    taskId = data.get("taskId")
                    page = data.get("page")
                    total_page = data.get("total_page")
                    sys_expect_quantity = data.get("sys_expect_quantity")
                    data_list = data.get("data_list")
                    types = data.get("type")
                    logging.info("save data start")
                    while True:
                        try:
                            RedisSaveToMongo(taskId=taskId, page=page, total_page=total_page, sys_expect_quantity=sys_expect_quantity, data_list=data_list, types=types).main()
                            break
                        except:
                            logging.error("Redis save to mongodb error:", traceback.format_exc())
                else:
                    sleep_time = random.randint(55, 65)
                    logging.info(f"waiting..........")
                    time.sleep(sleep_time)
        except:
            ddmessage(traceback.format_exc())


if __name__ == '__main__':
    pool = multiprocessing.Pool(process_num)
    logging.info(f"process number：{process_num}")
    for i in range(process_num):
        pool.apply_async(RedisSaveToMongo.run_save)
    pool.close()
    pool.join()
