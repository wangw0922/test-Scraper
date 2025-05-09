# coding=gbk
import sys
sys.path.append('....')
import datetime
import re
import time
import os
import json
import random
import ssl
import asyncio
import aiohttp
from aiohttp.client_exceptions import ClientHttpProxyError
import traceback
from scrapy import Selector
from xinwei.project.Collect.src.functions import get_edition
from xinwei.project.Collect.src.dd import ddmessage
from xinwei.project.Collect.src.loggerDefine import logger_define
from xinwei.project.Collect.src.verify import Verify
from xinwei.project.Collect.src.async_detail_paser import DetailParse
from xinwei.project.Collect.src.headers_list import headers_list
from xinwei.project.Control.app.api import Quit
from xinwei.project.setting import proxy, username, password, get_token_url, coroutine_num, cookies_and_headers_list, tunnel_name, machine_mark_code


my_logger = logger_define(os.getcwd(), 'asyncio')
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Aiohttp:
    def __init__(self, url_list, task_data=None):
        if task_data:
            self.task_data = task_data
        else:
            self.task_data = {}
        self.tunnel = proxy
        self.proxy_auth = aiohttp.BasicAuth(username, password)
        self.url_list = url_list
        self.data_list = []

    @staticmethod
    def get_ssl() -> ssl.SSLContext:
        """
        Modify fingerprint of tls
        """
        ORIGIN_CIPHERS = ('ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
                          'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES')
        ciphers = ORIGIN_CIPHERS.split(':')
        random.shuffle(ciphers)
        ciphers = ":".join(ciphers)
        ciphers = ciphers + ":!aNULL:!eNULL:!MD5"
        context = ssl.create_default_context()
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_TLSv1_1
        context.options |= ssl.OP_NO_TLSv1_2
        context.options |= ssl.OP_NO_TLSv1_3
        context.set_ciphers(ciphers)
        return context

    async def fetch(self, session, furl, sslgen) -> str:
        """
        Send asynchronous request
        """
        semaphore = asyncio.Semaphore(coroutine_num)
        async with semaphore:
            error_num = 0
            for i in range(50):
                result, message = Quit().verify(machine_code=machine_mark_code)
                if result == 0:
                    raise ZeroDivisionError("Exit...")
                while True:
                    try:
                        async with session.post(url=get_token_url, data={"tunnel_name": tunnel_name}) as token_res:
                            token_dict = await token_res.json(content_type='text/html', encoding='utf-8')
                            token = token_dict.get("token")
                            result = token_dict.get("result")
                    except:
                        my_logger.info("Request token exception，retry")
                        await asyncio.sleep(5)
                        continue
                    if result:
                        my_logger.info(f'-------------current token: {token}----------------')
                        break
                    else:
                        my_logger.info('Request overclocking,please waiting！')
                        await asyncio.sleep(61 - datetime.datetime.now().second + random.randint(1, 10))
                cookies_and_headers = random.choice(cookies_and_headers_list)
                a_cookies = cookies_and_headers.get('cookies')
                a_cookies['lc-main'] = "en_US"
                a_headers = random.choice(headers_list)
                if self.task_data.get('ua'):
                    a_headers['user-agent'] = self.task_data['ua']
                a_headers['downlink'] = str(float(random.choice(range(100, 2000, 5)) / 100))
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
                a_headers['dpr'] = str(random.choice(range(100, 200, 5)) / 100)
                a_headers['sec-ch-dpr'] = a_headers['dpr']
                a_headers[
                    'accept'] = f'text/html,application/xhtml+xml,application/xml;q={str(random.choice(range(6, 9)) / 10)},image/avif,image/webp,image/apng,*/*;q={str(random.choice(range(6, 9)) / 10)},application/signed-exchange;v=b3;q={str(random.choice(range(6, 9)) / 10)}'
                a_headers[
                    'accept-language'] = f'zh-CN,zh;q={str(random.choice(range(6, 9)) / 10)},en;q={str(random.choice(range(6, 9)) / 10)},en-GB;q={str(random.choice(range(6, 9)) / 10)},en-US;q={str(random.choice(range(6, 9)) / 10)}'
                a_headers['ect'] = random.choice(['3g', '4g', '5g'])
                a_headers['rtt'] = str(random.choice(range(100, 400, 50)))
                a_headers['viewport-width'] = str(random.choice(range(1080, 2400, 2)))

                # sslgen = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                # sslgen.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
                # sslgen.minimum_version = ssl.TLSVersion.TLSv1_2

                try:
                    async with session.get(url=furl, proxy="http://" + self.tunnel,
                                           proxy_auth=self.proxy_auth, ssl=sslgen,
                                           headers=a_headers, cookies=a_cookies, timeout=20) as response:
                        html = await response.text()
                except ClientHttpProxyError as e:
                    if e.__str__().__contains__("Bandwidth Over Limit"):
                        my_logger.info("Bandwidth Over Limit！！！")
                        await asyncio.sleep(10)
                        continue
                except Exception:
                    print(traceback.format_exc())
                    my_logger.error(f"Request exception,please retry {furl}")
                    await asyncio.sleep(i)
                    continue
                if response.status == 404:
                    return ""
                if response.status == 200 and len(html) > 20000:
                    sel = Selector(text=html)
                    txt = sel.css('#centerCol::text').get().strip()
                    if txt and re.findall("[\u4e00-\u9fa5]", txt):
                        my_logger.info(f"Text of detail data contain chinese")
                        with open(f"error_page\\chinese_page{str(random.randint(1,1000))}.html", "w", encoding="utf-8") as f:
                            f.write(html)
                        continue
                    return html
                elif response.status == 200 and len(html) < 20000:
                    html = await Verify().get_token(detaile_url=furl)
                    if html:
                        my_logger.info(f'Pass the verification! very good!!!---{len(html)}')
                        return html
                    else:
                        my_logger.info(f'Verification failed! i am sorry!!!')
                    with open('project\\Collect\\src\\ua.js', 'r') as f:
                        ua_list = json.load(f)
                    self.task_data['ua'] = random.choice(ua_list)
                    error_num += 1
                    my_logger.info(f'status:{response.status}---{len(html)}---url:{furl},')
                    if 30 > i >= 20:
                        my_logger.error('Agent exception')
                        time.sleep(i * 10)
                    elif i == 49:
                        ddmessage(
                            f'当前进程：{os.getpid()}代理异常重试结束\n出现验证码次数：{error_num}\n页面情况：{response.status}---{furl}')
                else:
                    my_logger.info(f'status:{response.status}---{len(html)}---url:{furl},')
                    await asyncio.sleep(i * 2.5)
                    continue
            my_logger.error(f'[{self.task_data.get("task_id")}]-[{self.task_data.get("seller_id")}]->End retry, ignored:{furl}')
            if error_num >= 20:
                ddmessage(
                    f'当前进程：{os.getpid()}代理异常重试结束\n出现验证码次数：{error_num}\n页面情况：{response.status}---{furl}')
            return ""

    async def main(self, page_url) -> None:
        """
        Running main
        """
        # aiohttp默认使用严格的HTTPS协议检查。可以通过将ssl设置为False来放松认证检查
        # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        sslgen = self.get_ssl()
        await asyncio.sleep(random.choice(range(50, 1550)) / 100)
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session=session, furl=page_url, sslgen=sslgen)
            if html:
                data = DetailParse(
                    url=page_url, response=html, task_data=self.task_data,
                    user_id=self.task_data.get('user_id'), task_id=self.task_data.get('task_id'),
                    exception_type=self.task_data.get('exception_type')).run_parse()
                self.data_list.append(data)
            else:
                my_logger.error(f'[{self.task_data.get("task_id")}]-[{self.task_data.get("seller_id")}]->详情页异常:{page_url}')
                data = DetailParse(
                    url=page_url, task_data=self.task_data,
                    user_id=self.task_data.get('user_id'), task_id=self.task_data.get('task_id'),
                    exception_type=17, remark='获取产品页面异常').run_parse()
                self.data_list.append(data)

    def run(self) -> list:
        """
        Run event loop
        """
        if self.url_list:
            get_edition()
            loop = asyncio.get_event_loop()
            tasks = [asyncio.ensure_future(self.main(url)) for url in self.url_list]
            loop.run_until_complete(asyncio.wait(tasks))
            return self.data_list
        else:
            my_logger.info(f'[{self.task_data.get("task_id")}]-[{self.task_data.get("seller_id")}]->Detail page of available is empty:{self.task_data.get("task_id")}')
