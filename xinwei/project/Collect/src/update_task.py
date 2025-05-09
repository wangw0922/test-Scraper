# coding=gbk
import sys
sys.path.append('....')
import os
import traceback
import pymongo
import datetime
import pymysql
from xinwei.project.Collect.src.loggerDefine import logger_define
from xinwei.project.setting import mysql_password, mysql_host, MongoClient, MongoDbName, machine_mark_code, mysql_port, \
    mysql_user

logging = logger_define(os.getcwd(), 'UpdateTask')


class UpdateTask(object):
    def __init__(self, taskId, page, total_page, sys_expect_quantity=0):
        self.taskId = taskId
        self.page = page
        self.total_page = total_page
        self.sys_expect_quantity = sys_expect_quantity
        while True:
            try:
                self.conn = pymysql.connect(
                    host=mysql_host,
                    port=mysql_port,
                    user=mysql_user,
                    password=mysql_password,
                    database='oms',
                    charset='utf8'
                )
                break
            except:
                logging.error(traceback.format_exc())
        self.cursor = self.conn.cursor()
        self.client = pymongo.MongoClient(MongoClient)
        self.db = self.client[MongoDbName]
        self.collections = self.db['collect_amazon_note']
        self.product_collection = self.db['collect_amazon_product']

    def __del__(self):
        while True:
            try:
                self.client.close()
                self.cursor.close()
                self.conn.close()
                break
            except:
                logging.error(traceback.format_exc())

    def update_task(self) -> None:
        """
        Update method
        """
        self.cursor.execute(f'select type from tb_collect_task where id="{self.taskId}"')
        task = self.cursor.fetchall()
        if task:
            task_type = task[0][0]
        else:
            logging.error(f"任务已删除--{self.taskId}")
            return
        if self.page == -1:
            end_time = datetime.datetime.now()
            sql = f'UPDATE tb_collect_task SET  end_time="{end_time}",status="2"  WHERE id={self.taskId};'
        else:
            cur_page = self.page
            total_page = self.total_page
            title_tort_quantity = len(self.collections.distinct('asin', {'taskId': self.taskId, 'primaryKey': True, 'exceptionType': 7}))
            no_grade_quantity = len(self.collections.distinct('asin', {'taskId': self.taskId, 'primaryKey': True, 'exceptionType': 3}))
            keyword_tort_quantity = len(self.collections.distinct('asin', {'taskId': self.taskId, 'primaryKey': True, 'exceptionType': 12}))
            brand_tort_quantity = len(self.collections.distinct('asin', {'taskId': self.taskId, 'primaryKey': True, 'exceptionType': 9}))
            classify_tort_quantity = len(self.collections.distinct('asin', {'taskId': self.taskId, 'primaryKey': True, 'exceptionType': 11}))
            product_error_quantity = len(self.collections.distinct('asin', {'taskId': self.taskId, 'primaryKey': True, 'exceptionType': 17}))
            asin_repeat_quantity = len(self.collections.distinct('asin', {'taskId': self.taskId, 'primaryKey': True, 'exceptionType': 19}))
            variant_quantity = len(self.collections.distinct('asin', {'taskId': self.taskId, 'primaryKey': True, 'isVariant': True, 'status': 1}))
            monomer_quantity = len(self.collections.distinct('asin', {'taskId': self.taskId, 'primaryKey': True, 'isVariant': False, 'status': 1}))
            suit_quantity = len(self.product_collection.distinct('asin', {'taskId': self.taskId, 'primaryKey': True}))
            sys_expect_quantity = self.sys_expect_quantity
            no_suit_quantity_total = sys_expect_quantity - suit_quantity
            machine_mark = machine_mark_code
            if cur_page == total_page:
                if task_type == 1:
                    sys_expect_quantity = suit_quantity + no_suit_quantity_total
                end_time = datetime.datetime.now()
                sql = f'UPDATE tb_collect_task SET  total_page="{total_page}",cur_page="{cur_page}",status="2",end_time="{end_time}",no_suit_quantity_total="{no_suit_quantity_total}",suit_quantity="{suit_quantity}",title_tort_quantity="{title_tort_quantity}",no_grade_quantity="{no_grade_quantity}",keyword_tort_quantity="{keyword_tort_quantity}",brand_tort_quantity="{brand_tort_quantity}",brand_tort_quantity="{brand_tort_quantity}",classify_tort_quantity="{classify_tort_quantity}",product_error_quantity="{product_error_quantity}",variant_quantity="{variant_quantity}",monomer_quantity="{monomer_quantity}",sys_expect_quantity="{sys_expect_quantity}",machine_mark="{machine_mark}",asin_repeat_quantity="{asin_repeat_quantity}"  WHERE id={self.taskId};'
            elif cur_page == 1:
                start_time = datetime.datetime.now()
                sql = f'UPDATE tb_collect_task SET  start_time="{start_time}",no_suit_quantity_total="{no_suit_quantity_total}",suit_quantity="{suit_quantity}",title_tort_quantity="{title_tort_quantity}",no_grade_quantity="{no_grade_quantity}",keyword_tort_quantity="{keyword_tort_quantity}",brand_tort_quantity="{brand_tort_quantity}",brand_tort_quantity="{brand_tort_quantity}",classify_tort_quantity="{classify_tort_quantity}",product_error_quantity="{product_error_quantity}",variant_quantity="{variant_quantity}",monomer_quantity="{monomer_quantity}",sys_expect_quantity="{sys_expect_quantity}",machine_mark="{machine_mark}",asin_repeat_quantity="{asin_repeat_quantity}"  WHERE id={self.taskId};'
            else:
                sql = f'UPDATE tb_collect_task SET  no_suit_quantity_total="{no_suit_quantity_total}",suit_quantity="{suit_quantity}",title_tort_quantity="{title_tort_quantity}",no_grade_quantity="{no_grade_quantity}",keyword_tort_quantity="{keyword_tort_quantity}",brand_tort_quantity="{brand_tort_quantity}",brand_tort_quantity="{brand_tort_quantity}",classify_tort_quantity="{classify_tort_quantity}",product_error_quantity="{product_error_quantity}",variant_quantity="{variant_quantity}",monomer_quantity="{monomer_quantity}",machine_mark="{machine_mark}",asin_repeat_quantity="{asin_repeat_quantity}"  WHERE id={self.taskId};'
        while True:
            try:
                self.cursor.execute(sql)
                self.conn.commit()
                break
            except:
                self.conn.rollback()
                logging.error(traceback.format_exc())

    @staticmethod
    def run_sql(sql) -> None:
        """
        Running mysql sentence
        """
        conn = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database='oms',
            charset='utf8'
        )
        cursor = conn.cursor()
        while True:
            try:
                cursor.execute(sql)
                conn.commit()
                cursor.close()
                conn.close()
                break
            except Exception:
                logging.error(traceback.format_exc())
                conn.rollback()
                logging.error(f"Running mysql sentence failed,wait for retry:{sql}---{traceback.format_exc()}")