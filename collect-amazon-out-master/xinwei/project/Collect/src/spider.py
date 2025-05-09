# coding=gbk
import sys
sys.path.append('....')
import datetime
import traceback
import os
import re
import time
import random
import json
from scrapy import Selector
import requests
from urllib.parse import urljoin
from lxml import etree
from xinwei.project.Collect.src.update_task import UpdateTask
from xinwei.project.Collect.src.update_page_error import update_mysql_and_mongo_page_exception_amount
from xinwei.project.Collect.src.async_detail_paser import DetailParse
from xinwei.project.Collect.src.functions import get_tort_data, push_data, get_edition
from xinwei.project.Collect.src.loggerDefine import logger_define
from xinwei.project.setting import machine_mark_code, get_all_userId_api, get_userId_api
# from xinwei.project.Collect.dd import ddmessage
from xinwei.project.Collect.src.async_request import Aiohttp
from xinwei.project.Collect.src.get_response import get_response


my_logger = logger_define(os.getcwd(), 'spider')


def get_data_list() -> list:
    """
    Get user id of all store manager
    """
    while True:
        try:
            url = f'{get_all_userId_api}/{machine_mark_code}'
            res = requests.get(url)
            data = res.json()['data']
            if len(data) > 0:
                data_set = set(data)
                result_list = [{'userId': userId, 'machineMark': machine_mark_code} for userId in data_set]
                return result_list
            else:
                my_logger.info(f'[{machine_mark_code}]->Request general task failed,waiting for retry')
                time.sleep(2)
                pass
        except:
            print(traceback.format_exc())
            my_logger.info(f'[{machine_mark_code}]->Request general task failed,waiting for retry')
            time.sleep(2)
            pass


def get_detail_list(response) -> list:
    """
    Obtain detail data on index page
    """
    sel = Selector(response=response)
    default_url = 'https://www.amazon.com'
    detail_list = []
    detail_intro_list = sel.css('div.s-main-slot.s-result-list.s-search-results.sg-row > div')
    if detail_intro_list and isinstance(detail_intro_list, list):
        for each_detail in detail_intro_list:
            try:
                price = float(each_detail.css('span.a-price > span.a-offscreen::text').get()[1:])
            except:
                price = None
            try:
                grade = float(re.search('(.+?)out', each_detail.css(
                    'span.a-icon-alt::text').get()).group(1))
            except:
                grade = None
            try:
                person = int(re.search(
                    '"a-size-base puis-light-weight-text s-link-centralized-style">(.+?)</span>',
                    each_detail.get()).group(1).replace(',', ''))
            except:
                person = None
            try:
                title = re.search('a-size-medium\sa-color-base\sa-text-normal">(.+?)</span>',
                                  each_detail.get()).group(1)
            except:
                title = None
            try:
                url = urljoin(default_url, re.search(
                    '"a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"\shref="(.+?)"',
                    each_detail.get()).group(
                    1))
            except:
                url = None
            if url:
                try:
                    asin = re.search('/dp/([A-Za-z\d]+)', url).group(1)
                except:
                    asin = None
                    my_logger.error(f'url error：{url}')
            else:
                asin = None
            detail_intro = {
                'price': price,
                'grade': grade,
                'person': person,
                'title': title,
                'url': url,
                'asin': asin
            }
            if detail_intro['url'] and asin:
                detail_list.append(detail_intro)
        return detail_list
    else:
        return detail_list


def screen_index(task_data: dict, detail_list: list) -> tuple:
    """
    Filter data of index page
    """
    screen_num = 0
    data_list = []
    # 遍历列表进行筛选，不合格的直接保存概要
    for each_detail in detail_list:
        if each_detail['price'] and each_detail['price'] < 3:
            # 筛选价格小于3美金的商品
            exception_type = 20
            remark = f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->商品价格低于标准：{each_detail["price"]}'
            my_logger.info(remark)
            data = DetailParse(
                url=each_detail['url'],
                user_id=task_data['user_id'],
                task_id=task_data['task_id'],
                remark=remark,
                exception_type=exception_type
            ).run_parse()
            data_list.append(data)
            detail_list.remove(each_detail)
            screen_num += 1
            continue
        if each_detail['grade'] and each_detail['grade'] < 2.5:
            # 筛选评分低于2.5的商品
            exception_type = 3
            remark = f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->商品评分低于标准：{each_detail["grade"]}'
            my_logger.info(remark)
            data = DetailParse(
                url=each_detail['url'],
                user_id=task_data['user_id'],
                task_id=task_data['task_id'],
                remark=remark,
                exception_type=exception_type
            ).run_parse()
            data_list.append(data)
            detail_list.remove(each_detail)
            screen_num += 1
            continue
    return detail_list, data_list


def collect_asin_set(task_list) -> None:
    """
    Collect task of item set
    """
    task_data = {'task_id': task_list.get('id'), 'user_id': task_list.get('userId'), 'exception_type': -1,
                 "orderby": task_list.get('orderby'), "is_first_task": task_list.get('is_first_task')}
    with open('project\\Collect\\src\\ua.js', 'r') as f:
        ua_list = json.load(f)
    ua = random.choice(ua_list)
    task_data['ua'] = ua
    length = len(set(task_list.get("itemIdList")))
    total_page = length // 10 + 1
    curPage = task_list.get('curPage')
    my_logger.info(f'{task_list.get("id")}->Get total number of asin:{length}')
    if curPage >= total_page:
        UpdateTask(taskId=task_list.get("id"), page=-1, total_page=length, sys_expect_quantity=length).update_task()
        my_logger.info(f"{task_list.get('id')}->End for task of item set,update data of task")
        return None
    detail_default_url = 'https://www.amazon.com/dp/{asin}/'
    detail_url_lists = [detail_default_url.format(asin=asin) for asin in set(task_list.get('itemIdList'))]
    for page in range(curPage+1, total_page+1):
        my_logger.info(f'[{task_data.get("task_id")}]->Task of item set in collection{(page-1)*10}-{page * 10}')
        detail_url_list = detail_url_lists[(page-1)*10:page*10]
        if detail_url_list:
            while True:
                try:
                    data_list = Aiohttp(url_list=detail_url_list, task_data=task_data).run()
                    redis_data = {
                        'type': 2,
                        "page": page,
                        "total_page": total_page,
                        "taskId": task_data['task_id'],
                        "sys_expect_quantity": length,
                        "data_list": data_list,
                        "is_first_task": task_list.get('is_first_task')
                    }
                    push_data(_data=redis_data)
                    my_logger.info(f'[{task_data.get("task_id")}]->Save data to redis：{(page-1)*10}-{page * 10}')
                    if page == 1:
                        start_time = datetime.datetime.now()
                        sql = f'UPDATE tb_collect_task SET  start_time="{start_time}",cur_page="{page}",total_page="{total_page}",status="1"  WHERE id={task_data.get("task_id")};'
                    else:
                        sql = f'UPDATE tb_collect_task SET  cur_page="{page}",total_page="{total_page}",status="1"  WHERE id={task_data.get("task_id")};'
                    UpdateTask.run_sql(sql)
                    break
                except ZeroDivisionError:
                    raise ZeroDivisionError("Exit...")
                except:
                    my_logger.error(f'[{task_data.get("task_id")}]->{traceback.format_exc()}')
        else:
            end_time = datetime.datetime.now()
            sql = f'UPDATE tb_collect_task SET total_page="{page}",end_time="{end_time}",status="2"  WHERE id={task_data.get("task_id")};'
            UpdateTask.run_sql(sql)
    my_logger.info(f'[{task_data.get("task_id")}]->End for task of item set,update data of task')
    end_time = datetime.datetime.now()
    sql = f'UPDATE tb_collect_task SET end_time="{end_time}",cur_page="{total_page}",total_page="{total_page}",status="2"  WHERE id={task_data.get("task_id")};'
    UpdateTask.run_sql(sql)


def start_requests(user_data: dict) -> dict:
    """
    Get task data of user
    """
    # 获取任务数据
    brand_tort = get_tort_data("brand_tort")
    # 获取品牌侵权信息
    title_tort = get_tort_data("title_tort")
    # 获取标题侵权信息
    keyword_tort = get_tort_data("keyword_tort")
    # 获取关键字侵权信息
    classic_tort = get_tort_data("classic_tort")
    # 获取分类侵权信息
    default_url = 'https://www.amazon.com/s?me={asin}&page=1&language=en_US'
    # 任务API
    url = get_userId_api
    data = user_data
    # 请求单个任务接口
    while True:
        try:
            my_logger.info('Requesting interface of task')
            task_list = requests.post(url=url, data=data).json()['data']
        except:
            task_list = []
            time.sleep(300)
            my_logger.info('Obtain task failed,wait for retry')
            continue
        if task_list and task_list.get('type') == 1:
            my_logger.info(f'{task_list.get("id")}->Succeeded in obtaining the store task')
            break
        elif task_list and task_list.get('type') == 2:
            my_logger.info(f'{task_list.get("id")}->Start collect task of item set')
            if task_list.get("itemIdList"):
                collect_asin_set(task_list)
                return {}
            else:
                my_logger.error(f'[{task_list.get("id", 0)}]->Task of item set is empty')
                return {}
        elif task_list and not task_list.get('type'):
            my_logger.info(f'{task_list.get("id")}->Obtain task successful,test environment')
            break
    # 获取任务数据
    if isinstance(task_list, dict):
        try:
            task_data = {
                'task_id': task_list.get('id'),
                'user_id': task_list.get('userId'),
                'cur_page': task_list.get('curPage'),
                'seller_id': task_list.get('sellerId').strip(),
                'url': default_url.format(asin=task_list.get('sellerId').strip().replace('&', '')),
                'brand_tort': brand_tort,
                'title_tort': title_tort,
                'keyword_tort.txt': keyword_tort,
                'classic_tort': classic_tort,
                'exception_type': 0,
                "orderby": task_list.get('orderby')
            }
            return task_data
        except:
            my_logger.info.error(f'Task error:{task_list.get("id")}')
            UpdateTask(taskId=task_list.get('id'), page=-1, total_page=150).update_task()
    else:
        my_logger.error('Task error')
        # 获取任务


def get_max_page(response: str, url: str, task_data: dict) -> int:
    """
    Obtain max number of page
    """
    my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Getting max number of page')
    if not os.path.exists(".\\error_page"):
        os.makedirs(".\\error_page")
    try:
        address = re.search('id="nav-global-location-popover-link"[\s\S]+</a>', response).group()
    except:
        my_logger.error(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->异常店铺，更新任务状态')
        with open(f'error_page//{task_data.get("seller_id")}_store_error.html', 'w', encoding="utf-8") as f:
            f.write(response)
        UpdateTask(taskId=task_data.get('task_id'), page=-1, total_page=-1, sys_expect_quantity=-1).update_task()
        raise AttributeError(f"Get address failed--{task_data.get('seller_id')}")
    if "China" in address or "中国" in address:
        while True:
            response = get_response(url, task_data=task_data).text
            address = re.search('id="nav-global-location-popover-link"[\s\S]+</a>', response).group()
            if "China" not in address:
                break
            else:
                my_logger.info(f"Address is China--{task_data.get('seller_id')}")
    # xpath获取节点
    htmls = etree.HTML(response)
    flag = htmls.xpath('//*[@id="search"]/span/div/h1/div/div[1]/div/div/span/text()')
    if not flag:
        try:
            flag = re.search('\d*?,*?\d+?-\d*?,*?\d+?\sof(.+?)results|\d+?\sresults', response).group()
        except:
            flag = None
    if flag:
        pages = htmls.xpath(
            '//div[@class="a-section a-text-center s-pagination-container"]//span[@class="s-pagination-item s-pagination-disabled"]/text()')
        if not pages:
            pages = htmls.xpath('//div[@class="a-section a-text-center s-pagination-container"]//span//a/text()')
            if not pages:
                pages = 1
            else:
                pages = int(pages[-2])
        else:
            pages = int(pages[0])
        return pages
    else:
        my_logger.error(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Shop error,update task data')
        with open(f'error_page//{task_data.get("seller_id")}_store_empty.html', 'w', encoding="utf-8") as f:
            f.write(response)
        UpdateTask(taskId=task_data.get('task_id'), page=-1, total_page=-1, sys_expect_quantity=0).update_task()
        raise AttributeError(f"Shop error,the shop is empty--{task_data.get('seller_id')}")


def scrape_save(one_page: int, default_index_url: str, task_data: dict, max_page: int) -> None:
    """
    Collect detail data and save
    """
    url = re.sub('&page=(\d+?)', f'&page={str(one_page)}', default_index_url)
    my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Requesting--{url}')
    # 获取列表页响应
    while True:
        index_response = get_response(url, task_data=task_data)
        try:
            address = re.search('id="nav-global-location-popover-link"[\s\S]+?</a>', index_response.text).group()
        except:
            continue
        if "China" in address or "中国" in address:
            my_logger.info(f"Address is China--{task_data.get('seller_id')}--{one_page}")
            continue
        else:
            break
    try:
        # 获取列表页左上角数据（商品总数估值）
        sys_expect_quantity = int(
            re.search('\d*?,*?\d+?-\d*?,*?\d+?\sof(.+?)results', index_response.text).group(1).replace('over',
                                                                                                       '').replace(
                ',', '').strip())
    except:
        sys_expect_quantity = 1
    if index_response:
        # 成功获取列表页响应
        my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Obtain data of index page')
        # 从列表页解析详情页数据
        detail_list = get_detail_list(response=index_response)
        my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Get number of product:{len(detail_list)}')
        if detail_list:
            my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Start filter')
            # 不合格商品筛选
            new_detail_list, index_data_list = screen_index(task_data=task_data, detail_list=detail_list)
            # 提取所有详情页url链接
            url_list = [each_detail['url'] for each_detail in new_detail_list]
            # 初步判断
            if len(url_list) != len(new_detail_list):
                my_logger.error(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Number exception{new_detail_list}\n{url_list}')
            if url_list:
                # 异步爬取该页所有详情信息
                while True:
                    try:
                        my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Start collect data of detail:{len(url_list)}')
                        data_list = Aiohttp(url_list=url_list, task_data=task_data).run()
                        data_list.extend(index_data_list)
                        # print(data_list)
                        redis_data = {
                            'type': 1,
                            "taskId": task_data['task_id'],
                            "page": one_page,
                            "total_page": max_page,
                            "sys_expect_quantity": sys_expect_quantity,
                            "data_list": data_list
                        }
                        push_data(_data=redis_data)
                        my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Save data to redis database successful  page:{one_page}, count:{len(data_list)}')
                        if one_page == 1:
                            start_time = datetime.datetime.now()
                            sql = f'UPDATE tb_collect_task SET  start_time="{start_time}",cur_page="{one_page}",total_page="{max_page}",status="1"  WHERE id={task_data.get("task_id")};'
                        else:
                            sql = f'UPDATE tb_collect_task SET  cur_page="{one_page}",total_page="{max_page}",status="1"  WHERE id={task_data.get("task_id")};'
                        UpdateTask.run_sql(sql)
                        break
                    except ZeroDivisionError:
                        raise ZeroDivisionError("Exit...")
                    except:
                        my_logger.error(traceback.format_exc())
            else:
                # 处理列表页无数据异常
                my_logger.error(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Current page have not product is available:{one_page}')
        else:
            my_logger.error(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Index page error,it is empty:{url}')
            with open(f'error_page//{task_data.get("seller_id")}_index_empty.html', 'w', encoding='utf-8') as f:
                f.write(index_response.text)
            # 保存异常页面
            while True:
                try:
                    update_mysql_and_mongo_page_exception_amount(taskId=task_data['task_id'], curPage=one_page,
                                                                 shop_url=url,
                                                                 userId=task_data['user_id'], page=one_page)
                    break
                except:
                    my_logger.error(traceback.format_exc())
                    continue


def scrape_index(default_index_url, task_data, shop_max_page) -> None:
    """
    Crawl for index page
    """
    # 根据cur_page,判断任务情况（新任务还是断点续爬）
    if task_data['cur_page'] == 0:
        my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->New task')
    else:
        my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Old task{task_data["cur_page"]}')
    if task_data['cur_page'] < shop_max_page:
        # 正常采集，根据最大页码构造所有列表页url，遍历爬取
        for each_page in range(task_data['cur_page'] + 1, shop_max_page + 1):
            my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Current page:{each_page}')
            # 开始爬取单独列表页
            scrape_save(one_page=each_page, default_index_url=default_index_url, task_data=task_data,
                        max_page=shop_max_page)
        # 遍历完成更新任务数据
        my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->End task,update data of task')
        sql = f'UPDATE tb_collect_task SET  cur_page="{shop_max_page}",total_page="{shop_max_page}",status="2"  WHERE id={task_data.get("task_id")};'
        UpdateTask.run_sql(sql)
    else:
        # 已完成任务，直接更新任务状态
        my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Task have completed,update task')
        UpdateTask(taskId=task_data['task_id'], page=-1, total_page=shop_max_page).update_task()


def run(user_data) -> None:
    """
    Running crawl
    """
    while True:
        # 验证版本号
        get_edition()
        # 获取请求UserAgent
        with open('project\\Collect\\src\\ua.js', 'r') as f:
            ua_list = json.load(f)
        ua = random.choice(ua_list)
        # 获取任务数据
        try:
            task_data = start_requests(user_data)
        except ZeroDivisionError:
            raise ZeroDivisionError("Exit...")
        if not task_data:
            my_logger.error("Task data cannot be empty,retry")
            continue
        my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Getting User-Agent')
        task_data['ua'] = ua
        first_url = task_data['url']
        sleep_time = random.choice([each / 10 for each in range(10, 50)])
        time.sleep(sleep_time)
        my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Obtain home page---{first_url}')
        # 获取店铺页响应
        try:
            first_response = get_response(first_url, task_data=task_data)
        except ZeroDivisionError:
            raise ZeroDivisionError("Exit...")
        if first_response:
            my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Getting max number of page')
            # 获取最大页码
            try:
                shop_max_page = get_max_page(response=first_response.text, url=first_url, task_data=task_data)
            except ZeroDivisionError:
                raise ZeroDivisionError("Exit...")
            except AttributeError:
                my_logger.info(f'[{os.getpid()}]->Address error,restart process: {traceback.format_exc()}')
                continue
            if shop_max_page:
                my_logger.info(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Start collect')
                # 进入店铺采集
            try:
                scrape_index(default_index_url=first_url, task_data=task_data, shop_max_page=shop_max_page)
            except ZeroDivisionError:
                raise ZeroDivisionError("Exit...")
            else:
                my_logger.error(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Page error,obtain max number of page failed')
                # 保存异常页面
                UpdateTask(taskId=task_data['task_id'], page=-1, total_page=150).update_task()
            # 刷新本地dns缓存
            os.system('ipconfig /flushdns')
        else:
            my_logger.error(f'[{task_data.get("task_id")}]-[{task_data.get("seller_id")}]->Page error,Obtain home page failed:{first_url}')


if __name__ == '__main__':
    a = get_data_list()
    print(a)
