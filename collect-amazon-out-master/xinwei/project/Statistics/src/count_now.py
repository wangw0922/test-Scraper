# coding=gbk
import sys
import pymysql
import pymongo
from xinwei.project.setting import MongoClient, MongoDbName, mysql_host, mysql_password, mysql_port, mysql_user
import time
import openpyxl
import datetime
from xinwei.project.Statistics.src.dd import ddmessage
import logging
import coloredlogs
sys.path.append('../')

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s:%(message)s')
coloredlogs.install(level='INFO')


def query(time_limit=None, time_end=None) -> None:
    """
    Statistics data of collect current
    """
    while True:
        now_time = datetime.datetime.now()
        logging.info(f'Statisticsing -> {now_time.strftime("%Y-%m-%d %H:%M:%S")}')
        start = time.time()
        _year, _month, _day = datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day
        if not time_limit:
            time_limit = datetime.datetime(_year, _month, _day)
        if not time_end:
            time_end = datetime.datetime.now()
        conn = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database='oms',
            charset='utf8'
        )
        try:
            cursor = conn.cursor()
            sql_str1 = f"SELECT COUNT(*) FROM tb_collect_task WHERE `status`=2 and end_time > '{time_limit}' and end_time < '{time_end}';"
            sql_str4 = f"SELECT COUNT(*) FROM tb_collect_task;"
            sql_str5 = f"SELECT COUNT(*) FROM tb_collect_task WHERE `status`=2;"
            cursor.execute(sql_str1)
            task_nums1 = cursor.fetchone()[0]
            cursor.execute(sql_str4)
            task_nums4 = cursor.fetchone()[0]
            cursor.execute(sql_str5)
            task_nums5 = cursor.fetchone()[0]
        except:
            logging.error(f"Mysql connection exception")
            continue
        task_nums6 = str(int((task_nums5 / task_nums4) * 100)) + "%"
        client = pymongo.MongoClient(MongoClient)
        db = client[MongoDbName]
        collections = db['collect_amazon_note']
        logging.info(f'Start time {time_limit}')
        logging.info(f'End time {time_end}')
        logging.info('Start search')
        logging.info('Looking for page error count')
        try:
            page_abnormal = collections.count_documents({'status': 0, 'createTime': {'$gt': time_limit, '$lt': time_end}})
            logging.info('Looking for asin of product count')
            asin_total = collections.count_documents(
                {'status': {'$in': [1, -1]}, 'createTime': {'$gt': time_limit, '$lt': time_end}})
            logging.info('Looking for asin of product count of effictive')
            effective = collections.count_documents({'status': 1, 'createTime': {'$gt': time_limit, '$lt': time_end}})
            logging.info('Looking for product count of torting')
            tort = collections.count_documents(
                {'status': 1, 'createTime': {'$gt': time_limit, '$lt': time_end}, 'exceptionType': {'$in': [7, 9, 11, 12]}})
            logging.info('Looking for product count of exception')
            abnormal = collections.count_documents(
                {'status': -1, 'createTime': {'$gt': time_limit, '$lt': time_end},
                 'exceptionType': {'$nin': [7, 9, 11, 12]}})
            logging.info('Looking for monomer count of effictive')
            Monomer_total = collections.count_documents(
                {'status': 1, 'createTime': {'$gt': time_limit, '$lt': time_end}, 'isVariant': False})
            logging.info('Looking for variant count of effictive and main')
            variant_primary = collections.count_documents(
                {'status': 1, 'createTime': {'$gt': time_limit, '$lt': time_end}, 'isVariant': True, 'primaryKey': True})
            logging.info('Statistics end....')
        except:
            logging.error(f"MongoDb connection exception")
            continue
        message_time = time_limit.strftime("%Y-%m-%d")
        message = f'{message_time}数据统计情况\n当日采集任务数:{task_nums1}\n异常页码数量:{page_abnormal}\nasin总数:{asin_total}\n有效asin总数:{effective}\n侵权数:{tort}\n异常数:{abnormal}\n商品总数（有效）:{Monomer_total + variant_primary}\n单体总数（有效）:{Monomer_total}\n变体主体总数（有效）:{variant_primary}\n任务总数:{task_nums4}\n已完成:{task_nums5}\n任务完成进度:{task_nums6}'
        ddmessage(text=message)
        data_list = [time_limit, time_end, task_nums1, page_abnormal, asin_total, effective, tort, abnormal,
                     Monomer_total + variant_primary,
                     Monomer_total, variant_primary, task_nums4, task_nums5, task_nums6]
        try:
            wb = openpyxl.load_workbook('count.xlsx')
            ws = wb.active
            ws.append(data_list)
            wb.save('count.xlsx')
        except:
            logging.error(f"Save statistics data exception")
            return None
        logging.info(f'Save statistics data successful')
        end = time.time()
        logging.info(f'Expend {end - start} second')


if __name__ == '__main__':
    year, month, day = datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day
    start_time = datetime.datetime(year, month, day)
    end_time = datetime.datetime.now()
    query(start_time, end_time)

