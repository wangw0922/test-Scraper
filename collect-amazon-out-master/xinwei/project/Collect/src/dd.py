import sys
sys.path.append('....')
import json
import datetime
import requests
from xinwei.project.setting import machine_mark_code


def ddmessage(text) -> None:
    """
    The interface use to send exception message on Dingding
    """
    url = "https://oapi.dingtalk.com/robot/send?access_token=dec4e37c3f71f9beb7e2525e0bc94fbe12f73a20dce580ace378a3ecf23eb03c"
    # url = "https://oapi.dingtalk.com/robot/send?access_token=b7ed108796af72702f7eff10330223e136d86402670bb7f303cd53e24996a3a1"
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    alldata = f'爬虫\n{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n机器：{machine_mark_code}\n{text}'
    # 构建请求数据，post请求
    data = {
        "msgtype": "text",
        "text": {
            "content": alldata  # 抓取数据发送的内容放到alldata
        },
        "at": {
            "isAtAll": True  # @全体成员（在此可设置@特定某人）
        }
    }
    # 对请求的数据进行json封装
    sendData = json.dumps(data)
    sendData = sendData.encode("utf-8")
    # 发送请求
    requests.post(url=url, data=sendData, headers=header)
    # 将请求发回的数据构建成为文件格式
    # opener = urllib.request.urlopen(request)

