import sys
sys.path.append('....')
import os
import random
import time
import json
import requests
from requests import Response
from xinwei.project.Control.app.api.whether_quit import Quit
from xinwei.project.Collect.src.functions import request_allow, get_edition
from xinwei.project.Collect.src.get_tls import get_tls
from xinwei.project.Collect.src.loggerDefine import logger_define
from xinwei.project.setting import username, password, proxy, headers, cookies_and_headers_list, machine_mark_code


logging = logger_define(os.getcwd(), 'GetResponse')


def get_response(_url: str, task_data=None, verify=True) -> Response:
    """
    Send request
    """
    if verify:
        result, message = Quit().verify(machine_code=machine_mark_code)
        if result == 0:
            raise ZeroDivisionError("Exit...")
    get_edition()
    r_proxy = f'http://{username}:{password}@{proxy}'
    proxies = {
        'http': r_proxy,
        'https': r_proxy
    }
    request_allow()
    while True:
        try:
            cookies_and_headers = random.choice(cookies_and_headers_list)
            a_cookies = cookies_and_headers.get('cookies')
            a_headers = headers
            if task_data:
                a_headers['user-agent'] = task_data.get('ua')
            a_headers['downlink'] = str(float(random.choice(range(50, 200, 5)) / 100))
            a_headers['sec-ch-ua'] = random.choice(['";Not A Brand";v="99", "Chromium";v="94"',
                                                    '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                                                    '"Google Chrome";v="104", "Chromium";v="104", "Not=A?Brand";v="81"',
                                                    '"Google Chrome";v="101", "Chromium";v="101", "Not=A?Brand";v="54"',
                                                    '"Google Chrome";v="99", "Chromium";v="99", "Not=A?Brand";v="51"',
                                                    '"Google Chrome";v="98", "Chromium";v="98", "Not=A?Brand";v="102"',
                                                    '"Google Chrome";v="96", "Chromium";v="96", "Not=A?Brand";v="45"',
                                                    '"Google Chrome";v="94", "Chromium";v="94", "Not=A?Brand";v="81"',
                                                    '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="159"',
                                                    '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="107"',
                                                    '"Google Chrome";v="91", "Chromium";v="91", "Not=A?Brand";v="124"',
                                                    '"Google Chrome";v="91", "Chromium";v="91", "Not=A?Brand";v="77"',
                                                    '"Google Chrome";v="105", "Chromium";v="105", "Not=A?Brand";v="19"',
                                                    '"Google Chrome";v="102", "Chromium";v="102", "Not=A?Brand";v="40"',
                                                    '"Google Chrome";v="100", "Chromium";v="100", "Not=A?Brand";v="20"',
                                                    '"Google Chrome";v="99", "Chromium";v="99", "Not=A?Brand";v="35"',
                                                    '"Google Chrome";v="97", "Chromium";v="97", "Not=A?Brand";v="20"',
                                                    '"Google Chrome";v="95", "Chromium";v="95", "Not=A?Brand";v="40"',
                                                    '"Google Chrome";v="93", "Chromium";v="93", "Not=A?Brand";v="51"',
                                                    '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="107"',
                                                    '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="70"',
                                                    '"Google Chrome";v="91", "Chromium";v="91", "Not=A?Brand";v="77"',
                                                    '"Google Chrome";v="106", "Chromium";v="106", "Not=A?Brand";v="6"',
                                                    '"Google Chrome";v="98", "Chromium";v="98", "Not=A?Brand";v="4"',
                                                    '"Google Chrome";v="94", "Chromium";v="94", "Not=A?Brand";v="12"',
                                                    '"Google Chrome";v="93", "Chromium";v="93", "Not=A?Brand";v="8"',
                                                    '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="20"',
                                                    '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="2"',
                                                    '"Google Chrome";v="93", "Chromium";v="93", "Not=A?Brand";v="4"',
                                                    '"Google Chrome";v="93", "Chromium";v="93", "Not=A?Brand";v="3"'])
            a_headers['viewport-width'] = str(random.choice(range(1024, 2400, 2)))
            a_headers['sec-ch-viewport-width'] = a_headers['viewport-width']
            a_headers['dpr'] = str(random.choice(range(10, 20)) / 10)
            a_headers['sec-ch-dpr'] = a_headers['dpr']
            a_headers['ect'] = random.choice(['3g', '4g', '5g'])
            a_headers['rtt'] = str(random.choice(range(100, 200, 50)))
            a_headers['accept-language'] = f'zh-CN,zh;q={str(random.choice(range(6, 9)) / 10)},en;q={str(random.choice(range(6, 9)) / 10)},en-GB;q={str(random.choice(range(6, 9)) / 10)},en-US;q={str(random.choice(range(6, 9)) / 10)}'
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:" + get_tls()
            _response = requests.get(_url, headers=a_headers, cookies=a_cookies, timeout=30, proxies=proxies)
        except:
            time.sleep(3.5)
            continue
        if _response.status_code == 200 and len(_response.text) > 10000:
            return _response
        elif "amazon" not in _url:
            return _response
        else:
            with open('project\\Collect\\ua.js', 'r') as f:
                ua_list = json.load(f)
            if task_data:
                task_data['ua'] = random.choice(ua_list)
            logging.info(f'Retry {_url}')
            logging.info(f'{_response.status_code}---{len(_response.text)}--{_url}')
            time.sleep(random.choice(range(50, 1050)) / 100)


if __name__ == '__main__':
    url = "https://www.baidu.com"
    response = get_response(url)
    print(len(response.text))
