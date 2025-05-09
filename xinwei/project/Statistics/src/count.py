# coding=gbk
import sys
sys.path.append('../')
import traceback
import time
import datetime
import logging
import coloredlogs
import openpyxl
import pymysql
import pymongo
from xinwei.project.Collect.src.dd import ddmessage
from xinwei.project.setting import MongoClient, MongoDbName, mysql_host, mysql_password, mysql_port, mysql_user

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s:%(message)s')
coloredlogs.install(level='INFO')


class DataStatistics(object):

    def __init__(self):
        self.conn = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database='oms',
            charset='utf8'
        )
        self.cursor = self.conn.cursor()
        self.client = pymongo.MongoClient(MongoClient)
        self.db = self.client[MongoDbName]
        self.collections = self.db['collect_amazon_note']
        self.wb = openpyxl.load_workbook('src/count.xlsx')
        self.ws = self.wb.active

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        self.client.close()
        self.wb.close()

    def query(self, time_limit=None, time_end=None) -> None:
        """
        Statistics data of collect regular
        """
        while True:
            now_time = datetime.datetime.now()
            logging.info(f'Statisticsing -> {now_time.strftime("%Y-%m-%d %H:%M:%S")}')
            start = time.time()
            year, month, day = datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day
            if not time_limit:
                time_limit = datetime.datetime(year, month, day)
            if not time_end:
                time_end = datetime.datetime.now()
            try:
                sql_str1 = f"SELECT COUNT(*) FROM tb_collect_task WHERE `status`=2 and end_time > '{time_limit}' and end_time < '{time_end}';"
                sql_str4 = f"SELECT COUNT(*) FROM tb_collect_task;"
                sql_str5 = f"SELECT COUNT(*) FROM tb_collect_task WHERE `status`=2;"
                self.cursor.execute(sql_str1)
                task_nums1 = self.cursor.fetchone()[0]
                self.cursor.execute(sql_str4)
                task_nums4 = self.cursor.fetchone()[0]
                self.cursor.execute(sql_str5)
                task_nums5 = self.cursor.fetchone()[0]
            except:
                print(traceback.format_exc())
                logging.error(f"Mysql connection exception")
                continue
            task_nums6 = str(int((task_nums5 / task_nums4) * 100)) + "%"
            format_str = "%Y-%m-%d %H:%M:%S"
            logging.info(f'Start time {time_limit.strftime(format_str)}')
            logging.info(f'End time {time_end.strftime(format_str)}')
            logging.info('Start search')
            try:
                logging.info('Looking for page error count')
                page_abnormal = self.collections.count_documents({'status': 0, 'createTime': {'$gt': time_limit, '$lt': time_end}})
                logging.info('Looking for asin of product count')
                asin_total = self.collections.count_documents(
                    {'status': {'$in': [1, -1]}, 'createTime': {'$gt': time_limit, '$lt': time_end}})
                logging.info('Looking for asin of product count of effictive')
                effective = self.collections.count_documents({'status': 1, 'createTime': {'$gt': time_limit, '$lt': time_end}})
                logging.info('Looking for product count of torting')
                tort = self.collections.count_documents(
                    {'status': 1, 'createTime': {'$gt': time_limit, '$lt': time_end}, 'exceptionType': {'$in': [7, 9, 11, 12]}})
                logging.info('Looking for product count of exception')
                abnormal = self.collections.count_documents(
                    {'status': -1, 'createTime': {'$gt': time_limit, '$lt': time_end},
                     'exceptionType': {'$nin': [7, 9, 11, 12]}})
                logging.info('Looking for monomer count of effictive')
                Monomer_total = self.collections.count_documents(
                    {'status': 1, 'createTime': {'$gt': time_limit, '$lt': time_end}, 'isVariant': False})
                logging.info('Looking for variant count of effictive and main')
                variant_primary = self.collections.count_documents(
                    {'status': 1, 'createTime': {'$gt': time_limit, '$lt': time_end}, 'isVariant': True, 'primaryKey': True})
                logging.info('Statistics end....')
            except:
                logging.error(f"MongoDb connection exception")
                continue
            if datetime.datetime.now().hour in [9, 12, 16, 20, 00]:
                message_time = time_limit.strftime("%Y-%m-%d")
                message = f'{message_time}数据统计情况\n当日采集任务数:{task_nums1}\n异常页码数量:{page_abnormal}\nasin总数:{asin_total}\n有效asin总数:{effective}\n侵权数:{tort}\n异常数:{abnormal}\n商品总数（有效）:{Monomer_total + variant_primary}\n单体总数（有效）:{Monomer_total}\n变体主体总数（有效）:{variant_primary}\n任务总数:{task_nums4}\n已完成:{task_nums5}\n任务完成进度:{task_nums6}'
                ddmessage(text=message)
            data_list = [time_limit, time_end, task_nums1, page_abnormal, asin_total, effective, tort, abnormal,
                         Monomer_total + variant_primary,
                         Monomer_total, variant_primary, task_nums4, task_nums5, task_nums6]
            try:
                self.ws.append(data_list)
                self.wb.save('src/count.xlsx')
            except:
                logging.error(f"Save statistics data exception")
                return None
            logging.info(f'Save statistics data successful')
            end = time.time()
            logging.info(f'Expend {end - start} second')
            return

    def daily_count(self):
        while True:
            try:
                while True:
                    now_time = datetime.datetime.now()
                    sleep_time = 58 - now_time.second if now_time.second < 58 else 118 - now_time.second
                    if (now_time.hour % 4 == 3 and now_time.minute == 59) or (
                            now_time.hour == 18 and now_time.minute == 29):
                        self.query()
                    elif now_time.hour == 9 and now_time.minute == 00:
                        times = datetime.datetime.now()
                        time_limit = datetime.datetime(times.year, times.month, times.day - 1)
                        time_end = datetime.datetime(times.year, times.month, times.day)
                        self.query(time_limit=time_limit, time_end=time_end)
                    else:
                        logging.info(f'Waiting.....')
                        # self.query()
                        time.sleep(sleep_time)
            except Exception:
                logging.error(f'Save statistics data failure')
                logging.error(traceback.format_exc())


if __name__ == '__main__':
    DataStatistics().daily_count()
