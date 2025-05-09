# -*- coding: utf-8 -*-
# @Time    : 2023/1/17 10:15
# @Author  : 李文霖
import json

from flask import request

from . import QUIT_BLU, Q


class QuitApi(object):

    @staticmethod
    @QUIT_BLU.route("/status_verify", methods=['post'])
    def verify() -> json:
        """
        Request method: POST

        Data example: {"machine_code": 192.168.2.31}

        Return: json data
        """
        machine_code = request.form.get("machine_code")
        result, message = Q.verify(machine_code)
        return json.dumps({'result': result, "message": message}, ensure_ascii=False)

    @staticmethod
    @QUIT_BLU.route("/get_all_status", methods=['get'])
    def get_all() -> json:
        """
        Request method: GET

        Return: json data
        """
        result, message = Q.get_all()
        return json.dumps({'result': result, "message": message}, ensure_ascii=False)

    @staticmethod
    @QUIT_BLU.route("/end_status", methods=['post'])
    def end() -> json:
        """
        Request method: POST

        Data example: {"machine_code": 192.168.2.31}

        Return: json data
        """
        machine_code = request.form.get("machine_code")
        result, message = Q.end(machine_code=machine_code)
        return json.dumps({'result': result, "message": message}, ensure_ascii=False)

    @staticmethod
    @QUIT_BLU.route("/start_status", methods=['post'])
    def start() -> json:
        """
        Request method: POST

        Data example: {"machine_code": 192.168.2.31}

        Return: json data
        """
        machine_code = request.form.get("machine_code")
        result, message = Q.start(machine_code=machine_code)
        return json.dumps({'result': result, "message": message}, ensure_ascii=False)
