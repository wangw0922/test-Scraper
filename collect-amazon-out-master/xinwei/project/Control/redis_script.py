# -*- coding: utf-8 -*-
# @Time    : 2023/3/2 9:34
# @Author  : 李文霖

import pickle
from redis import StrictRedis

HOST = "127.0.0.1"
PORT = 6379
PASSWORD = ""
DATABASE = 5


def main():
    service = StrictRedis(host=HOST, port=PORT, password=PASSWORD, db=DATABASE)
    agent_configuration = {
        '192.168.2.31': 'tunnel1', '192.168.2.2': 'T5', '50': 'tunnel3', '52': 'tunnel3', '49': 'tunnel3',
        '51': 'tunnel3', '33': 'tunnel3', '47': 'tunnel3', '53': 'tunnel3', '54': 'tunnel3', '56': 'tunnel3',
        '57': 'tunnel3', '48': 'tunnel3', '32': 'tunnel3', '55': 'tunnel3', '192.168.2.100': 'tunnel1'
    }
    agent_information = {
        'tunnel1': {
            'address': 'l260.kdltps.com:15818', 'user_name': 't16858003800994', 'password': 'q6fait7q',
            'request_frequency': '500'
        }, 'tunnel2': {
            'address': 'j156.kdltps.com:15818', 'user_name': 't16808145322187', 'password': 'yoo1oj7o',
            'request_frequency': '290'
        }, 'tunnel3': {
            'address': 'w195.kdltps.com:15818', 'user_name': 't16929075122555', 'password': 'tw54a5vu',
            'request_frequency': '290'
        }, 'tunnel4': {
            'address': 'n188.kdltps.com:15818', 'user_name': 't17117452122472', 'password': 'syuyj59h',
            'request_frequency': '290'
        }, 'T5': {
            'address': 'm514.kdltps.com:15818', 'user_name': 't17512922688869', 'password': 'gyb9pm4t',
            'request_frequency': '250'
        }
    }
    service.set("AgentConfiguration", pickle.dumps(agent_configuration))
    service.set("AgentInformation", pickle.dumps(agent_information))
    service.close()


if __name__ == '__main__':
    main()
