import sys
sys.path.append('....')
import datetime
import os
import traceback
import hashlib
from redis import StrictRedis
import pymongo
from xinwei.project.Collect.src.loggerDefine import logger_define
from xinwei.project.setting import redis_host, redis_port, redis_password


logging = logger_define(os.getcwd(), 'BloomFilter')
BLOOMFILTER_BIT = 30
BLOOMFILTER_HASH_NUMBER = 6


class HashMap(object):
    def __init__(self, m, seed):
        self.m = m
        self.seed = seed

    def hash(self, value) -> int:
        """
        Generate hash fuction
        """
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.m - 1) & ret


class BlooFilter(object):
    """
    Bloom Filter class
    """
    def __init__(self):
        self.m = 1 << BLOOMFILTER_BIT
        self.seeds = range(BLOOMFILTER_HASH_NUMBER)
        self.maps = [HashMap(self.m, seed) for seed in self.seeds]
        self.server = StrictRedis(host=redis_host, port=redis_port, password=redis_password)
        self.key = "BloomFilter"

    def exists(self, value) -> int:
        """
        Determine whether it is existed
        """
        if not value:
            return False
        exist = 1
        md_value = hashlib.md5(value.encode('utf8')).hexdigest()
        for each_map in self.maps:
            offset = each_map.hash(md_value)
            exist = exist & self.server.getbit(self.key, offset)
        return exist

    def insert(self, value) -> None:
        """
        Save to bloom filter
        """
        md_value = hashlib.md5(value.encode('utf8')).hexdigest()
        for f in self.maps:
            offset = f.hash(md_value)
            self.server.setbit(self.key, offset, 1)


def add_bloom() -> None:
    """
    Insert old data
    """
    while True:
        try:
            db = pymongo.MongoClient("mongodb://root:xinwei2020@198.11.173.2:27018")
            client = db["Collect"]
            collections = client["collect_amazon_product"]
            time_limit = datetime.datetime(datetime.datetime.now().year - 1, datetime.datetime.now().month, datetime.datetime.now().day)
            logging.info(time_limit)
            total = collections.find({'createTime': {'$gt': time_limit}})
            logging.info("开始添加")
            for each in total:
                asin = each.get("asin")
                if not BlooFilter().exists(asin):
                    BlooFilter().insert(asin)
                    logging.info(f"{datetime.datetime.now()}--成功添加：{asin}")
                else:
                    logging.info(f"{datetime.datetime.now()}--重复asin：{asin}")
            break
        except:
            logging.error(traceback.format_exc())
            continue



if __name__ == '__main__':
    bf = BlooFilter()
    logging.info(bf.exists("B01AE63JN4"))
