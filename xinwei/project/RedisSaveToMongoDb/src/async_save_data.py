# coding=gbk
import sys

sys.path.append('../')
import os
import time
import traceback
from hashlib import md5
from pymongo.errors import ServerSelectionTimeoutError, BulkWriteError, DuplicateKeyError
from xinwei.project.RedisSaveToMongoDb.src.asin_repeat import repeat_asin
from xinwei.project.setting import MongoClient, MongoDbName
from motor.motor_asyncio import AsyncIOMotorClient
from xinwei.project.Collect.src.loggerDefine import logger_define

logging = logger_define(os.getcwd(), 'async_save_data')


class AsyncMongoData:
    def __init__(self, data_list):
        self.data_list = data_list
        self.db = AsyncIOMotorClient(MongoClient)
        self.client = self.db[MongoDbName]
        self.collection_detail = self.client['collect_amazon_product']
        self.collection_profile = self.client['collect_amazon_note']
        self.collection_asins = self.client['collect_amazon_asins']

    @staticmethod
    def get_token(deomo_val) -> str:
        """
        Generate id（mongodb）
        """
        md5_val = md5(deomo_val.encode('utf8')).hexdigest()
        return md5_val

    async def save_detail(self) -> None:
        """
        Save detail data
        """
        detail_data_list = [each_data.get('data') for each_data in self.data_list if each_data.get("data")]
        while True:
            try:
                if detail_data_list and detail_data_list != [None]:
                    await self.collection_detail.insert_many(detail_data_list)
                    logging.info(f'Save detail data successful--{len(detail_data_list)}')
                    break
                else:
                    break
            except (BulkWriteError, DuplicateKeyError):
                logging.info(f"Id of detail data is repeating--{[each.get('_id') for each in detail_data_list]}")
                break
            except ServerSelectionTimeoutError:
                logging.error('Save detail data failed,waiting for retry')
                time.sleep(3)
            except:
                logging.error(
                    f'Save detail data failed,waiting for retry\n{detail_data_list}\n{traceback.format_exc()}')
                time.sleep(3)
                continue

    async def save_profile(self) -> None:
        """
        Save profile data
        """
        profile_data_list = [each_data.get('profile') for each_data in self.data_list if each_data.get("profile")]
        while True:
            try:
                if profile_data_list and profile_data_list != [None]:
                    await self.collection_profile.insert_many(profile_data_list)
                    logging.info(f'Save profile data successful--{len(profile_data_list)}')
                    break
                else:
                    break
            except (BulkWriteError, DuplicateKeyError):
                logging.info(f"Id of profile data is repeating--{[each.get('_id') for each in profile_data_list]}")
                break
            except ServerSelectionTimeoutError:
                logging.error('Save profile data failed,waiting for retry')
                time.sleep(3)
            except:
                logging.error(
                    f'Save profile data failed,waiting for retry\n{profile_data_list}\n{traceback.format_exc()}')
                time.sleep(3)
                continue

    def save_asins(self, profile_data_dict) -> None:
        """
        Save asins data
        """
        while True:
            try:
                self.collection_asins.insert_one(profile_data_dict)
                break
            except (BulkWriteError, DuplicateKeyError):
                logging.info(f"Id of profile data is repeating--{[each.get('_id') for each in profile_data_dict]}")
                break
            except ServerSelectionTimeoutError:
                logging.error('Save profile data failed,waiting for retry')
                time.sleep(3)
            except:
                logging.error(
                    f'Save profile data failed,waiting for retry\n{profile_data_dict}\n{traceback.format_exc()}')
                time.sleep(3)
                continue
    async def run(self) -> None:
        """
        Running method
        """
        for data in self.data_list:
            if not data.get("data"):
                """
                await self.save_profile()
                """
                self.db.close()
                return
            if data.get("data").get("primaryKey"):
                task_id = data.get("profile").get("taskId")
                """
                result = await repeat_asin(data.get('data').get('asin'), task_id)
                if result:
                    profile = data.get("profile")
                    profile['remark'] = f"Asin repeating:{data.get('data').get('asin')}-{data.get('data').get('taskId')}"
                    logging.info(profile['remark'])
                    profile["exceptionType"] = 19
                    profile["status"] = -1
                    profile["isCollect"] = False
                    self.data_list = [{'data': None, 'profile': profile}]
                """
                await self.save_detail()
                """
                await self.save_profile()
                """
                self.db.close()
                return
        logging.error(f"Save data exception,primary key is empty->{self.data_list}")
