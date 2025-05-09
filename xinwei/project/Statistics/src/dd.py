import sys
import requests
import json
import datetime
sys.path.append('../')


def ddmessage(text) -> None:
    """
    Dingding api
    """
    url = "https://oapi.dingtalk.com/robot/send?access_token=b7ed108796af72702f7eff10330223e136d86402670bb7f303cd53e24996a3a1"

    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    alldata = f"{datetime.datetime.now()}\n爬虫数据报告\n{text}"
    # 构建请求数据，post请求
    data = {
        "msgtype": "text",
        "text": {
            "content": alldata  # 抓取数据发送的内容放到alldata
        },
    }
    # 对请求的数据进行json封装
    sendData = json.dumps(data)
    sendData = sendData.encode("utf-8")
    # 发送请求
    requests.post(url=url, data=sendData, headers=header)
    # 将请求发回的数据构建成为文件格式
    # opener = urllib.request.urlopen(request)
