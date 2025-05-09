#!D:\soft\api api
# -*- coding: utf-8 -*-
# @Time    : 2022/12/4 21:08
# @Author  : 杨硕
# @File    : get_redis_data.py
# @Software: win11 Software Parser api 3.8.6
import sys

sys.path.append('./')
import redis
from setting import redis_host, redis_port, redis_password


class ClientRedis:
    def __init__(self):
        self.client = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=5)
        self.name = 'uspsList'

    def get_redis_data(self):
        length = self.client.llen(self.name)
        if length and length < 1000:
            length = length
        elif length and length >= 1000:
            length = 1000
        else:
            return None
        results = self.client.lrange(self.name, 0, length - 1)
        tLabels_lists = []
        for result in results:
            tLabels_lists.append(result.decode('utf-8').replace('"', ''))
        return tLabels_lists

    def drop_track(self, track):
        result = self.client.lrem(name=self.name, count=0, value=f'"{track}"')
        return result

