import json
from flask import request
from . import edition_blu, TA


class Edition(object):

    @staticmethod
    @edition_blu.route("/verify_edition", methods=['post'])
    def VerifyEdition() -> json:
        """
        Request method: POST

        Data example: form-data  {"edition": 2.08}

        Return: json data
        """
        your_edition = request.form.get("edition")
        result, current_edition = TA.getEdition()
        if str(your_edition) == str(current_edition):
            return json.dumps({'pass': True, "latest edition": current_edition, "message": "验证通过"}, ensure_ascii=False)
        elif not your_edition:
            return json.dumps({'pass': False, "latest edition": current_edition, "message": "验证不通过，版本号不能为空"}, ensure_ascii=False)
        else:
            return json.dumps({'pass': False, "latest edition": current_edition, "message": f"验证不通过,请跟新至最新版本-{current_edition}"}, ensure_ascii=False)

    @staticmethod
    @edition_blu.route("/set_edition", methods=['post'])
    def SetEdition() -> json:
        """
        Request method: POST

        Data example: {"edition": 2.08}

        Return: json data
        """
        try:
            edition = float(request.form.get("edition"))
        except ValueError:
            return json.dumps({'result': False, "message": "输入的版本格式不正确"}, ensure_ascii=False)
        result, message = TA.setEdition(edition)
        return json.dumps({'result': result, "message": message}, ensure_ascii=False)

    @staticmethod
    @edition_blu.route("/update_edition", methods=['get'])
    def UpdateEdition() -> json:
        """
        Request method: GET

        Return: json data
        """
        result, message = TA.updateEdition()
        return json.dumps({'result': result, "message": message}, ensure_ascii=False)
