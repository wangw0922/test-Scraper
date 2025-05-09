import json
from flask import request
from . import agent_blu, TA


class AgentControl(object):

    @staticmethod
    @agent_blu.route("/get_agent_configuration", methods=['get'])
    def getAgentConfiguration() -> json:
        """
        Get configuration of tunnel agent and machine code

        Url: http://127.0.0.1:5001/get_agent_configuration

        Request method: GET

        Return: json data
        """
        result, data = TA.getAgentConfiguration()
        return json.dumps({"result": result, "data": data}, ensure_ascii=False)

    @staticmethod
    @agent_blu.route("/get_agent_information", methods=['get'])
    def getAgentInformation() -> json:
        """
        Get information of tunnel agent

        Url: http://127.0.0.1:5001/get_agent_information

        Request method: GET

        Return: json data
        """
        result, data = TA.getAgentInformation()
        return json.dumps({"result": result, "data": data}, ensure_ascii=False)

    @staticmethod
    @agent_blu.route("/set_agent_configuration", methods=['post'])
    def setAgentConfiguration() -> json:
        """
        Set configuration of tunnel agent and machine code

        Url: http://127.0.0.1:5001/set_agent_configuration

        Request method: POST

        Data example: {"machine_code": "192.168.2.31", "tunnel_name": "tunnel1"}

        Return: json data
        """
        machine_code = request.form.get("machine_code")
        tunnel_name = request.form.get("tunnel_name")
        result, message = TA.setAgentConfiguration(machine_code=machine_code, tunnel_name=tunnel_name)
        return json.dumps({"result": result, "message": message}, ensure_ascii=False)

    @staticmethod
    @agent_blu.route("/set_agent_information", methods=['post'])
    def setAgentInformation() -> json:
        """
        Modify information of tunnel agent

        Url: http://127.0.0.1:5001/set_agent_information

        Request method: POST

        Data example: {"tunnel_name": "tunnel1", "address": "l260.kdltps.com:15818", "user_name": "t16858003800994","password": "q6fait7q","request_frequency": 290}

        Return: json data
        """
        tunnel_name = request.form.get("tunnel_name")
        address = request.form.get("address")
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        request_frequency = request.form.get("request_frequency")
        result, message = TA.setAgentInformation(tunnel_name=tunnel_name, address=address, user_name=user_name, password=password, request_frequency=request_frequency)
        return json.dumps({"result": result, "message": message}, ensure_ascii=False)

    @staticmethod
    @agent_blu.route("/delete_configuration", methods=['post'])
    def deleteConfiguration() -> json:
        """
        Delete configuration of tunnel agent and machine code

        Url: http://127.0.0.1:5001/delete_configuration

        Request method: POST

        Data example: {"machine_code": "192.168.2.31"}

        Return: json data
        """
        machine_code = request.form.get("machine_code")
        result, message = TA.deleteConfiguration(machine_code)
        return json.dumps({"result": result, "message": message}, ensure_ascii=False)

    @staticmethod
    @agent_blu.route("/delete_information", methods=['post'])
    def deleteInformation() -> json:
        """
        Delete tunnel agent

        Url: http://127.0.0.1:5001/delete_information

        Request method: POST

        Data example: {"tunnel_name": "tunnel5"}

        Return: json data
        """
        tunnel_name = request.form.get("tunnel_name")
        result, message = TA.deleteInformation(tunnel_name)
        return json.dumps({"result": result, "message": message}, ensure_ascii=False)
