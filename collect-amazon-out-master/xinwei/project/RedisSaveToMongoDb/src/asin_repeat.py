import sys

sys.path.append('../')
import os
import time
import traceback
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from xinwei.project.setting import MongoClient, MongoDbName
from xinwei.project.Collect.src.dd import ddmessage
from xinwei.project.Collect.src.loggerDefine import logger_define

logging = logger_define(os.getcwd(), 'asin_repeat')


async def repeat_asin(asin, task_id) -> bool:
    """
    Asynchronous search duplicate asin of product in mongodb 去重 重复返回True
    """
    client = AsyncIOMotorClient(MongoClient)
    db = client[MongoDbName]
    collection = db['collect_amazon_product']
    year, month, day = datetime.datetime.now().year - 1, datetime.datetime.now().month, datetime.datetime.now().day
    time_limit = datetime.datetime(year, month, day)
    while True:
        error_num = 0
        try:
            numbers = await collection.count_documents({'asin': asin})
            if numbers >= 4:
                return True
            status = await collection.find_one({'asin': asin, "taskId": task_id})
            if status:
                if status.get("status") == -100:
                    collection.delete_one({"_id": status.get("_id")})
                    return False
                return True
            else:
                return False
        except:
            logging.error(f"Repeating error {traceback.format_exc()}")
            error_num += 1
            if error_num >= 50:
                ddmessage(text=traceback.format_exc())
                time.sleep(60)




# if __name__ == '__main__':
#         client = AsyncIOMotorClient(MongoClient)
#         db = client[MongoDbName]
#         collection = db['collect_amazon_product']
#         year, month, day = datetime.datetime.now().year - 1, datetime.datetime.now().month, datetime.datetime.now().day
#         time_limit = datetime.datetime(year, month, day)
#         a={'asin': "B09LCQYQG4", "userId": 33, "createTime": {"$gt": time_limit}}
#         data=list(collection.find_one(a)
#         print(data)
