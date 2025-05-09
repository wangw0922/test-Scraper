# coding=gbk
import sys
sys.path.append('....')
import datetime
import pymongo
import pymysql
from xinwei.project.setting import mysql_password, mysql_host, MongoClient, MongoDbName, machine_mark_code, mysql_port, \
    mysql_user


def update_mysql_and_mongo_page_exception_amount(taskId, curPage, shop_url, userId, page) -> None:
    """
    Update data of index error
    """
    conn = pymysql.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database='oms',
        charset='utf8'
    )
    db = pymongo.MongoClient(MongoClient)
    # 异常列表页更新到mongo
    client = db[MongoDbName]
    collection_profile = client['collect_amazon_note']
    data = {
        'remake': '列表页异常',
        'status': 0,
        'type': 2,
        'isVariant': True,
        'primaryKey': None,
        'parentUuid': None,
        'asin': None,
        'link': shop_url,
        'userId': userId,
        'taskId': taskId,
        'createTime': datetime.datetime.now(),
        'class': 'com.xinwei.common.mongo.mo.CollectAmazonNoteMO',
        'exceptionType': 18,
        'machine_mark': machine_mark_code
    }
    collection_profile.insert_one(data)
    # 异常列表页更新到mysql
    cursor = conn.cursor()
    select_sql = f'SELECT page_error_amount FROM tb_collect_task WHERE id={taskId};'
    cursor.execute(select_sql)
    page_error_amount = cursor.fetchone()[0]
    if not page_error_amount:
        page_error_amount = 0
    page_error_amount_nums = page_error_amount + 1
    start_time = datetime.datetime.now()
    machine_mark = machine_mark_code
    if curPage:
        updat_sql = f'UPDATE tb_collect_task SET cur_page="{page}",page_error_amount="{page_error_amount_nums}",status="{1}",machine_mark="{machine_mark}" WHERE id={taskId};'
    else:
        updat_sql = f'UPDATE tb_collect_task SET cur_page="{page}",page_error_amount="{page_error_amount_nums}",status="{1}",start_time="{start_time}",machine_mark="{machine_mark}" WHERE id={taskId};'
    try:
        cursor.execute(updat_sql)
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
