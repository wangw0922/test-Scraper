from . import token_blu, TA
import json
from flask import request


class Token(object):

    @staticmethod
    @token_blu.route('/get_token', methods=['post'])
    def getToken() -> json:
        """
        Request method: POST

        Data example: {"tunnel_name": "tunnel1"}

        Return: json data
        """
        tunnel_name = request.form.get('tunnel_name')
        result, token = TA.getToken(tunnel_name)
        return json.dumps({"result": result, "token": token}, ensure_ascii=False)
