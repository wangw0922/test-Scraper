# -*- coding: utf-8 -*-
# @Time    : 2023/1/17 10:20
# @Author  : 李文霖
import pickle
import redis


REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = "xinwei2020"


class Quit(object):

    def __init__(self):
        self.serve = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=5)

    def verify(self, machine_code) -> tuple:
        try:
            status_dict = pickle.loads(self.serve.get("status")) if self.serve.get("status") else None
        except Exception as e:
            return False, f"error: {e}"
        result = status_dict.get(machine_code)
        if result == 1:
            return True, "Continue"
        else:
            return False, "Exit"


    def get_all(self) -> tuple:
        try:
            status_dict = pickle.loads(self.serve.get("status")) if self.serve.get("status") else None
        except Exception as e:
            return False, f"error: {e}"
        if status_dict:
            return True, status_dict
        else:
            return False, "Data is empty"

    def start(self, machine_code) -> tuple:
        try:
            status_dict = pickle.loads(self.serve.get("status")) if self.serve.get("status") else None
        except Exception as e:
            return False, f"error: {e}"
        if status_dict:
            status_dict[machine_code] = 1
        else:
            status_dict = {machine_code: 1}
        try:
            self.serve.set("status", pickle.dumps(status_dict))
        except Exception as e:
            return False, f"error: {e}"
        return True, "ok"

    def end(self, machine_code) -> tuple:
        try:
            status_dict = pickle.loads(self.serve.get("status")) if self.serve.get("status") else None
        except Exception as e:
            return False, f"error:{e}"
        if status_dict:
            status_dict[machine_code] = 0
        else:
            status_dict = {machine_code: 0}
        try:
            self.serve.set("status", pickle.dumps(status_dict))
        except Exception as e:
            return False, f"error{e}"
        return True, "ok"
