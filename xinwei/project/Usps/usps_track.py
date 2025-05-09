#!D:\soft\api api
# -*- coding: utf-8 -*-
# @Time    : 2022/12/2 10:39
# @Author  : 杨硕
# @File    : request.py
# @Software: win11 Software Parser api 3.8.6
# !D:\soft\api api
# -*- coding: utf-8 -*-
# @Time    : 2022/11/30 10:14
# @Author  : 杨硕
# @File    : tort_update_main.py
# @Software: win11 Software Parser api 3.8.6
import os
import sys
import traceback

from xinwei.project.Usps.get_redis_data import ClientRedis
from xinwei.project.Usps.get_response import GetResponse

sys.path.append('../../../../../Documents/WeChat Files/wxid_v61ewyyfapms21/FileStorage/File/2023-01/')
import time
from lxml import etree
from conversion_time import conversion_time
from threading import Thread
import requests
import json
from setting import callback_url
from loggerDefine import logger_define
from dd import ddmessage

logger = logger_define(os.getcwd(), 'usps_track')


class GetTrackData:
    def __init__(self):
        self.callback_headers = {
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Content-Type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        }
        self.callback_url = callback_url

    def callback(self, track_list):
        """
        Dict transform data of json
        """
        track_data = json.dumps(track_list)
        number = str(track_list[0].get('number'))
        for API_error_num in range(5):
            try:
                r = requests.post(url=self.callback_url, data=track_data, headers=self.callback_headers,
                                  timeout=20).json()
                code = r.get('code')
                if code == 200:
                    logger.info(f'Order number:[{number}],The callback API succeeded')
                    break
                if API_error_num == 4:
                    ddmessage(f'Retry:{API_error_num}次,订单号{number}')
            except Exception:
                logger.error(f'API错误,订单号{number},{traceback.format_exc()}')
        for drop_num in range(5):
            if number:
                try:
                    result = ClientRedis().drop_track(number)
                    if result:
                        logger.info(f'redis单号删除成功,删除的单号为[{number}]')
                        break
                    else:
                        logger.error(f'redis单号删除失败,失败的单号为[{number}]')
                except Exception:
                    logger.error(f'redis单号删除失败,失败的单号为[{number}]{traceback.format_exc()}')
                    continue
            if drop_num == 4:
                ddmessage(f'redis单号删除失败,重试次数{drop_num}次失败,失败的单号为[{number}]')

    def detail_parse(self, content):
        """解析页面 """
        track_data = etree.HTML(content)
        track_data_xpaths_list = track_data.xpath('/html/body//div[@class="product_summary"]')
        logger.info(f'页面响应成功，本页物流单号数量为{len(track_data_xpaths_list)}')
        for track_data_xpaths in track_data_xpaths_list:
            track_detail = {'number': track_data_xpaths.xpath('.//div[@class="tracking-wrapper"]/span/@value')[0]}
            track_detail_datas = track_data_xpaths.xpath(
                './/div[contains(@class,"tracking-progress-bar-status-container")]/div')
            logistics_node_list = []
            for track_detail_data in track_detail_datas:
                try:
                    logistics_node_dict = {}
                    try:
                        logistics_node_dict['event'] = \
                            track_detail_data.xpath('.//p[@class="tb-status-detail"]/text()')[
                                0].replace('\n', '').replace('\t', '').replace('\xa0', '').replace(' ', '')
                    except Exception:
                        logistics_node_dict['event'] = None

                    try:
                        location = track_detail_data.xpath('.//p[@class="tb-location"]/text()')[0].replace('\n',
                                                                                                           '').replace(
                            '\xa0', '').strip()
                        if location:
                            logistics_node_dict['address'] = location
                        else:
                            logistics_node_dict['address'] = None
                    except Exception:
                        logistics_node_dict['address'] = None
                    try:
                        shop = track_detail_data.xpath('.//p[@class="tb-date"]/text()[2]')[0].replace('\n', '').replace(
                            '\t', '').replace(' ', '').replace('\xa0', '').split(':')[1]
                        if shop:
                            logistics_node_dict['event'] += ' by ' + shop
                    except:
                        pass
                    time_str = track_detail_data.xpath('.//p[@class="tb-date"]/text()')[0].replace('\n', '').replace(
                        '\t',
                        '').replace(
                        ' ', '').replace('\xa0', '')
                    logistics_node_dict['date'] = conversion_time(time_str)
                    logistics_node_list.append(logistics_node_dict)
                except Exception:
                    pass
            if not logistics_node_list:
                number = track_detail.get('number')
                logger.error(f'订单号不正确或者未发货,订单号为[{number}]')
            track_detail['track'] = {'trailList': logistics_node_list}
            self.callback([track_detail])

    def get_track_data(self, track_url):
        """拿到响应"""
        start_time = int(time.time())
        while True:
            now_time = int(time.time())
            if now_time - start_time > 500:
                logger.error(f'等待超时,等待时间为{now_time - start_time}秒,失败的ulr链接为[{track_url}]')
                ddmessage(f'等待超时,等待时间为{now_time - start_time}秒,失败的ulr链接为[{track_url}]')
                break
            try:
                content = GetResponse().get_post_response(track_url=track_url)

                self.detail_parse(content)
                break
            except Exception:
                try:
                    content = GetResponse().get_get_response(track_url=track_url)
                    self.detail_parse(content)
                    break
                except Exception:
                    continue

    @staticmethod
    def get_tLabels_lists():
        try:
            """拿到订单"""
            tLabels_lists = ClientRedis().get_redis_data()
            return tLabels_lists
        except Exception:
            return []

    @staticmethod
    def get_track_url_lists(tLabels_lists):
        """拿到订单拼接url 35个订单为一组"""
        track_url_lists = []
        while True:
            track_numbers = []
            for i in range(35):
                if not tLabels_lists:
                    break
                track_numbers.append(tLabels_lists.pop())
            track_start_url = 'https://tools.usps.com/go/TrackConfirmAction?tRef=fullpage&tLc=16&text28777=&tLabels='
            for track_number in track_numbers:
                track_start_url += str(track_number) + '%2c'
            track_end_url = track_start_url + '&tABt=false'
            track_url_lists.append(track_end_url)
            if not tLabels_lists:
                break
        return track_url_lists

    def run(self):
        """启动爬虫"""
        tLabels_lists = self.get_tLabels_lists()
        if tLabels_lists:
            logger.info(f'获取物流单号成功，获取单号数量[{len(tLabels_lists)}]')
            track_url_lists = self.get_track_url_lists(tLabels_lists)
            T = []
            for track_url in track_url_lists:
                t = Thread(target=GetTrackData().get_track_data, args=(track_url,))
                T.append(t)
            for t in T:
                t.start()
            for j in T:
                j.join()


if __name__ == '__main__':
    GetTrackData().run()
