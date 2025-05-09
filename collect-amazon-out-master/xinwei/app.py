# coding=gbk
import sys
import threading
import _tkinter
import os
import re
import traceback
import tkinter.font as tkFont
import pymysql
import requests
from PIL import ImageTk
from PIL import Image as imim
from tkinter import *

from redis.client import StrictRedis

from project.setting import machine_mark_code, redis_host, redis_port, redis_password, redis_db, \
    get_agent_configuration, get_agent_information, get_all_userId_api, mysql_port, mysql_user, redis_data_collection, \
    developer_password, post_edition_url, set_edition_url, update_edition_url, set_agent_configuration, \
    delete_agent_configuration, set_anget_information, delete_agent_information
import easygui as eg
from xinwei.project.Collect.src.functions import get_edition
# from xinwei.project.Collect.run_spider import run_crawl
from xinwei.project.Control.app.api.whether_quit import Quit
from xinwei.save_main import save_main

sys.path.append('../')


def stor_crawl(parent_root: Tk) -> None:
    Quit().end(machine_code=machine_mark_code)
    parent_root.destroy()


class App(object):

    def __init__(self):
        self.other_root = None
        self.file_str = None
        self.concurrency = None
        self.process = None
        self.password = None
        self.machine_code = None
        self.old_process_num = None
        self.old_machine_mark_code = None
        self.old_coroutine_num = None
        self.root = Tk()
        self.root.geometry("900x600+500+150")
        self.root.resizable(False, False)
        self.en_root = None
        with open('project/Collect/src/edition.py', 'r', encoding='utf-8') as f:
            edition_str = f.read()
        self.edition = re.search("edition\s=\s(.+)", edition_str).group(1).replace('"', '').strip()
        self.root.title(f'Scrape--{self.edition}')
        self.ft1 = tkFont.Font(family='Fixdsys', size=25, weight=tkFont.BOLD)
        self.ft2 = tkFont.Font(family='Fixdsys', size=15, weight=tkFont.BOLD)
        self.ft3 = tkFont.Font(family='Fixdsys', size=10, weight=tkFont.BOLD)

    def __del__(self):
        redis_service = StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=redis_db)
        redis_service.set("crawl_process_number", 0)
        redis_service.set("save_process_number", 0)
        redis_service.close()

    @staticmethod
    def in_crawl() -> None:
        root = Tk()
        root.resizable(False, False)
        root.title('提示')
        root.geometry("500x250+720+330")
        Label(root, text=f'数据采集中...', font=('华文新魏', 16)).pack(
            padx=20, pady=20)
        Button(root, text='停止', font=('华文新魏', 16), height=2, width=5, command=lambda: stor_crawl(root)).place(relx=0.4, rely=0.7)
        root.mainloop()

    @staticmethod
    def in_save() -> None:
        root = Tk()
        root.resizable(False, False)
        root.title('提示')
        root.geometry("500x250+720+330")
        Label(root, text=f'数据保存中...', font=('华文新魏', 16)).pack(
            padx=20, pady=20)
        Button(root, text='停止', font=('华文新魏', 16), height=2, width=5, command=lambda: stor_crawl(root)).place(relx=0.4,
                                                                                                              rely=0.7)
        root.mainloop()

    @staticmethod
    def run_crawl() -> None:
        """
        Running spider
        """
        os.system("python project\\Collect\\crawl_main.py")
        # try:
        #     response = get_edition()
        #     if response.get('pass'):
        #         t2 = threading.Thread(target=self.in_crawl)
        #         t2.start()
        #         t1 = threading.Thread(target=run_crawl)
        #         t1.start()
        #     else:
        #         root = Toplevel(self.root)
        #         root.resizable(False, False)
        #         root.title('提示')
        #         root.geometry("500x250+720+330")
        #         Label(root, text=f'当前版本--{self.edition}\n\n已过期，请更新至最新版--{response.get("edition")}', font=('华文新魏', 16)).pack(padx=20, pady=20)
        #         Button(root, text='ok', font=self.ft1, height=2, width=5, command=root.destroy).pack(padx=3, pady=50)
        # except Exception as e:
        #     self.tipsWiondow(self.root, f"error:{e}\n{traceback.format_exc()}")

    @staticmethod
    def start_save():
        os.system(f'python project\\RedisSaveToMongoDb\\save_main.py')

    def run_save(self) -> None:
        """
        Running save data
        """
        try:
            response = get_edition()
            if response.get('pass'):
                t2 = threading.Thread(target=self.in_save)
                t2.start()
                t1 = threading.Thread(target=save_main)
                t1.start()
            else:
                root = Toplevel(self.root)
                root.resizable(False, False)
                root.title('提示')
                root.geometry("500x250+720+330")
                Label(root, text=f'当前版本--{self.edition}\n\n已过期，请更新至最新版--{response.get("edition")}', font=('华文新魏', 16)).pack(padx=20, pady=20)
                Button(root, text='ok', font=self.ft1, height=2, width=5, command=root.destroy).pack(padx=3, pady=50)
        except Exception as e:
            self.tipsWiondow(self.root, f"error:{e}\n{traceback.format_exc()}")

    def save_setting(self, parent_root) -> None:
        """
        Save private setting
        """
        try:
            while True:
                machine_code_str = self.machine_code.get()
                process_str = str(self.process.get())
                concurrency_str = str(self.concurrency.get())
                if machine_code_str != self.old_machine_mark_code:
                    agent_configuration = requests.get(get_agent_configuration).json().get("data")
                    agent_information = requests.get(get_agent_information).json().get("data")
                    machine_code_list = agent_configuration.keys()
                    if machine_code_str not in machine_code_list:
                        raise ValueError("Machine code is unavailable")
                    _tunnel_name = agent_configuration.get(machine_code_str)
                    _username = agent_information.get(_tunnel_name).get("user_name")
                    _password = agent_information.get(_tunnel_name).get("password")
                    _proxy = agent_information.get(_tunnel_name).get("address")
                    try:
                        res = requests.get(f'{get_all_userId_api}/{machine_code_str}')
                    except:
                        raise ValueError(f'Network connection exception：{traceback.format_exc()}')
                    if not res.json()['data']:
                        raise ValueError("User name error")
                    a_proxy = f'http://{_username}:{_password}@{_proxy}'
                    proxies = {
                        'http': a_proxy,
                        'https': a_proxy
                    }
                    try:
                        res = requests.get('https://dev.kdlapi.com/testproxy', proxies=proxies)
                    except:
                        raise ValueError(f'Tunnel agent is unavailable\n\n\n{traceback.format_exc()}')
                    if res.status_code != 200:
                        raise ValueError(f'Tunnel agent is unavailable--status_code={res.status_code}')
                new_file_str = self.file_str.replace(f'machine_mark_code = "{self.old_machine_mark_code}"',
                                                     f'machine_mark_code = "{machine_code_str}"').replace(
                    f'coroutine_num = {self.old_coroutine_num}', f'coroutine_num = {concurrency_str}').replace(
                    f'process_num = {self.old_process_num}', f'process_num = {process_str}')
                try:
                    with open(f'project\\setting.py', 'w', encoding='utf-8') as s:
                        s.write(new_file_str)
                except:
                    raise ValueError(f'Setting save failed:\n\n\n{traceback.format_exc()}')
                roots = Toplevel(parent_root)
                roots.resizable(False, False)
                roots.title('success!!')
                roots.geometry("350x200+700+350")
                Label(roots, text='配置保存成功', font=('华文新魏', 18),
                      justify=LEFT).place(relx=0.3, rely=0.1)
                Button(roots, text='确定', font=('华文新魏', 15), command=parent_root.destroy).place(relx=0.45, rely=0.75)
                break
        except Exception as e:
            self.tipsWiondow(self.root, f"error:{e}\n" + traceback.format_exc())

    @staticmethod
    def tipsWiondow(root, words: str, size="big") -> None:
        """
        Tips window
        """
        roots = Toplevel(root)
        roots.resizable(False, False)
        roots.title('Tips')
        width, height = 45, 19
        roots.geometry("580x400+700+250")
        if size == 'small':
            roots.geometry("400x300+700+250")
            width, height = 30, 10
        text = Text(roots, font=('华文新魏', 15), width=width, height=height, relief=SUNKEN, wrap=WORD)
        text.place(relx=0.03, rely=0.01)
        text.insert(END, words)
        text.config(state="disabled")
        Button(roots, text='确定', font=('华文新魏', 15), command=roots.destroy).place(relx=0.45, rely=0.85)

    def modify(self, parent_root) -> None:
        """
        Private setting

        Set information of tunnel agent,machine code and number of concurrent coroutine and process
        """
        with open(f'project\\setting.py', 'r', encoding='utf-8') as f:
            self.file_str = f.read()
        self.old_machine_mark_code = re.search('machine_mark_code\s*?=\s?(.+)', self.file_str).group(1).replace('"',
                                                                                                                '').replace(
            "'", '')
        self.old_process_num = re.search('process_num\s*?=\s?(.+)', self.file_str).group(1)
        self.old_coroutine_num = re.search('coroutine_num\s*?=\s?(.+)', self.file_str).group(1)
        root = Toplevel(parent_root)
        root.resizable(False, False)
        root.title('爬虫设置')
        root.geometry("700x400+600+230")
        Label(root, text='请输入要修改的内容，保存后退出\n保存过程需要等待一段时间', font=('华文新魏', 18)).place(relx=0.25, rely=0.02)
        Label(root, text='用户ID:', font=('华文新魏', 18)).place(relx=0.1, rely=0.2)
        self.machine_code = Entry(root, width=25, font=('仿宋', 18))
        self.machine_code.insert(0, self.old_machine_mark_code)
        self.machine_code.place(relx=0.35, rely=0.2)
        Label(root, text='进程数量:', font=('华文新魏', 18)).place(relx=0.1, rely=0.4)
        var1 = IntVar()
        var2 = DoubleVar()
        self.process = Scale(root, orient=HORIZONTAL, length=310, from_=1, to=15, tickinterval=2, resolution=1,
                             variable=var1)
        self.process.set(int(self.old_process_num))
        self.process.place(relx=0.34, rely=0.36)
        Label(root, text='并发数量:', font=('华文新魏', 18)).place(relx=0.1, rely=0.6)
        self.concurrency = Scale(root, orient=HORIZONTAL, length=310, from_=2, to=16, tickinterval=2, resolution=1,
                                 variable=var2)
        self.concurrency.set(int(self.old_coroutine_num))
        self.concurrency.place(relx=0.34, rely=0.56)
        Button(root, text='保存设置', command=lambda: self.save_setting(root), font=('华文新魏', 19), width=8, height=2).place(relx=0.4, rely=0.8)
        Button(root, text='退出', command=root.destroy, font=('华文新魏', 19), relief=RAISED, width=8,
               overrelief="sunken").place(relx=0.8, rely=0.85)
        root.mainloop()

    def install_python(self) -> None:
        """
        Quick installation api
        """
        root = Toplevel(self.root)
        root.resizable(False, False)
        root.title('安装python')
        root.geometry("800x500+580+220")
        Label(root, text='1、如果你的电脑已安装python可以直接退出\n\n2、如有疑问可点击左下角查看文档\n\n3、请在确认安装完成后退出', font=('华文新魏', 16),
              justify=LEFT).place(relx=0.23, rely=0.1)
        Button(root, text='开始安装', command=lambda: os.system('start project\\python-3.8.6-amd64.exe'), font=('华文新魏', 19),
               relief=RAISED, overrelief="sunken", height=2, width=10).place(relx=0.4, rely=0.5)
        Button(root, text='不懂，点我查看文档', command=lambda: os.system('start project\\words\\python_install.docx'),
               font=('华文新魏', 15), relief=FLAT, overrelief="sunken").place(relx=0.03, rely=0.85)
        Button(root, text='退出', command=root.destroy, font=('华文新魏', 19), relief=RAISED, width=8,
               overrelief="sunken").place(relx=0.8, rely=0.85)
        root.mainloop()

    def install_environment(self) -> None:
        """
        Install requirements
        """
        root = Toplevel(self.root)
        root.resizable(False, False)
        root.title('设置')
        root.geometry("800x500+580+220")
        Label(root, text='1、在此之前，请确定本机已经安装好了python\n\n2、这个过程可能需要等待一段时间\n\n3、如有疑问可点击左下角查看文档\n\n4、请在确认安装完成后退出',
              font=('华文新魏', 16), justify=LEFT).place(relx=0.22, rely=0.1)
        Button(root, text='开始安装虚拟环境', command=self.environment_start, font=('华文新魏', 19),
               relief=RAISED, overrelief="sunken", width=15, height=2).place(relx=0.35, rely=0.5)
        Button(root, text='退出', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
               overrelief="sunken", height=2).place(relx=0.80, rely=0.85)
        Button(root, text='不懂，点我查看文档', command=lambda: os.system('start project\\words\\environment_install.docx'),
               font=('华文新魏', 15), relief=FLAT, width=16,
               overrelief="sunken", height=2).place(relx=0.03, rely=0.85)
        root.mainloop()

    @staticmethod
    def environment_start() -> None:
        """
        Run instruction of install requirments
        """
        os.system('pip install -r project\\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple')

    def test(self) -> None:
        """
        Set collected environment to test
        """
        try:
            with open(f'project\\setting.py', 'r', encoding='utf-8') as f:
                file_str = f.read()
            new_str = file_str.replace('redis_db = 1', 'redis_db = 2').replace('redis_data_db = 3',
                                                                               'redis_data_db = 4').replace('生产环境',
                                                                                                            '测试环境')
            with open(f'project\\setting.py', 'w', encoding='utf-8') as f:
                f.write(new_str)
            root = Toplevel(self.en_root)
            root.resizable(False, False)
            root.title('Tips')
            root.geometry("300x150+830+350")
            Label(root, text='修改成功!!\n\n当前采集环境为测试环境', font=('华文新魏', 16)).pack(padx=20, pady=20)
            Button(root, text='ok', font=self.ft1, height=4, width=4, command=self.en_root.destroy).pack(padx=3, pady=5)
        except Exception as e:
            self.tipsWiondow(self.root, f"error:{e}\n{traceback.format_exc()}")

    def produce(self) -> None:
        """
        Set collected environment to produce
        """
        try:
            with open(f'project\\setting.py', 'r', encoding='utf-8') as f:
                file_str = f.read()
            new_str = file_str.replace('redis_db = 2', 'redis_db = 1').replace('redis_data_db = 4',
                                                                               'redis_data_db = 3').replace('测试环境',
                                                                                                            '生产环境')
            with open(f'project\\setting.py', 'w', encoding='utf-8') as f:
                f.write(new_str)
            root = Toplevel(self.en_root)
            root.resizable(False, False)
            root.title('提示')
            root.geometry("300x150+830+350")
            Label(root, text='修改成功!!\n\n当前采集环境为生产环境', font=('华文新魏', 16)).pack(padx=20, pady=20)
            Button(root, text='ok', font=self.ft1, height=4, width=4, command=self.en_root.destroy).pack(padx=3, pady=5)
        except Exception as e:
            self.tipsWiondow(self.root, f"error:{e}\n{traceback.format_exc()}")

    def build(self) -> None:
        """
        Build environment of running
        """
        root = Toplevel(self.root)
        root.resizable(False, False)
        root.title('搭建环境')
        root.geometry("800x500+550+185")
        Label(root, text='第一步：安装python\n\n第二步：安装虚拟环境\n\n请按照顺序操作，完成后退出', font=('华文新魏', 16)).place(relx=0.3, rely=0.1)
        Button(root, text='安装python', command=self.install_python, font=('华文新魏', 19),
               relief=RAISED, overrelief="sunken", width=12, height=2).place(relx=0.35, rely=0.4)
        Button(root, text='安装虚拟环境', command=self.install_environment, font=('华文新魏', 19), relief=RAISED, width=12,
               overrelief="sunken", height=2).place(relx=0.35, rely=0.6)
        Button(root, text='退出', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
               overrelief="sunken", height=2).place(relx=0.80, rely=0.85)
        root.mainloop()

    def choice_en(self) -> None:
        """
        Choice collected enviroument
        """
        with open(f'project\\setting.py', 'r', encoding='utf-8') as f:
            file_str = f.read()
        old_db = re.search('redis_db\s*?=\s?(.+)', file_str).group(1).replace("'", '')
        if old_db == '1':
            en = '当前采集环境:生产环境'
        else:
            en = '当前采集环境:测试环境\n\n提示:店长请选择生产环境'
        self.en_root = Toplevel(self.root)
        self.en_root.resizable(False, False)
        self.en_root.title('设置采集环境')
        self.en_root.geometry("800x500+580+220")
        Label(self.en_root, text=en, font=('华文新魏', 16),
              justify=LEFT).place(relx=0.34, rely=0.1)
        Button(self.en_root, text='测试环境', command=self.test,
               font=('华文新魏', 19), relief=RAISED, overrelief="sunken", width=9, height=2).place(relx=0.4, rely=0.35)
        Button(self.en_root, text='生产环境', command=self.produce, font=('华文新魏', 19), relief=RAISED, width=9,
               overrelief="sunken", height=2).place(relx=0.4, rely=0.6)
        Button(self.en_root, text='退出', command=self.en_root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
               overrelief="sunken", height=2).place(relx=0.80, rely=0.85)
        self.en_root.mainloop()

    def setting(self) -> None:
        """
        This is a buttom that be use fo Setting
        """
        root = Toplevel(self.root)
        root.resizable(False, False)
        root.title('设置')
        root.geometry("800x500+550+185")
        Label(root, text='1、设置采集环境：可选择生产环境和测试环境\n\n2、爬虫设置：设置进程数、协程数和用户ID', font=('华文新魏', 16),
              justify=LEFT).place(relx=0.23, rely=0.1)
        Button(root, text='设置采集环境', command=self.choice_en, font=('华文新魏', 19), relief=RAISED,
               overrelief="sunken", width=12, height=2).place(relx=0.35, rely=0.4)
        Button(root, text='爬虫设置', command=lambda: self.modify(root), font=('华文新魏', 19), relief=RAISED, width=12,
               overrelief="sunken", height=2).place(relx=0.35, rely=0.6)
        Button(root, text='完成', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
               overrelief="sunken", height=2).place(relx=0.80, rely=0.85)
        root.mainloop()

    def show_setting(self) -> None:
        """
        View information of setting current
        """
        with open(f'project\\setting.py', 'r', encoding='utf-8') as f:
            file_str = f.read()
        old_machine_mark_code = re.search('machine_mark_code\s*?=\s?(.+)', file_str).group(1).replace('"', '')
        current_proxy = requests.get(get_agent_configuration).json().get("data").get(old_machine_mark_code, "tunnel1")
        old_process_num = re.search('process_num\s*?=\s?(.+)', file_str).group(1)
        old_coroutine_num = re.search('coroutine_num\s*?=\s?(.+)', file_str).group(1)
        old_db = re.search('redis_db\s*?=\s?(.+)', file_str).group(1).replace("'", '')
        _redis_data_db = re.search('redis_data_db\s*?=\s?(.+)', file_str).group(1).replace("'", '')
        _server = StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=int(old_db))
        _mysql_host = str(_server.get("mysql_host"), encoding="utf-8")
        _mysql_password = str(_server.get("mysql_password"), encoding="utf-8")
        _server.close()
        conn = pymysql.connect(
            host=_mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=_mysql_password,
            database='oms',
            charset='utf8'
        )
        try:
            cursor = conn.cursor()
            in_collection_sql = f"SELECT COUNT(*) FROM tb_collect_task WHERE `status`=1;"
            cursor.execute(in_collection_sql)
            in_collection = cursor.fetchone()[0]
            to_be_collected_sql = f"SELECT COUNT(*) FROM tb_collect_task WHERE `status`=0;"
            cursor.execute(to_be_collected_sql)
            to_be_collected = cursor.fetchone()[0]
            cursor.close()
            conn.close()
        except:
            self.tipsWiondow(root=self.root, words="Mysql connection exception", size="small")
            return
        redis_service = StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=int(_redis_data_db))
        data_number = redis_service.llen(redis_data_collection)
        redis_service.close()
        if old_db == '1':
            en = '生产环境'
        else:
            en = '测试环境'
        root = Toplevel(self.root)
        root.resizable(False, False)
        root.title('当前配置信息')
        root.geometry("800x500+550+185")
        Label(root,
              text=f'采集环境：{en}\n\n机器编码：{old_machine_mark_code}\n\n当前隧道：{current_proxy}\n\n进程数量：{old_process_num}'
                   f'\n\n并发数量：{old_coroutine_num}\n\n待采集：{to_be_collected} 个\n\n采集中：{in_collection} 个'
                   f'\n\n待保存：{data_number} 页', font=('华文新魏', 16), justify=LEFT).place(relx=0.3, rely=0.1)
        Button(root, text='退出', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
               overrelief="sunken", height=2).place(relx=0.80, rely=0.85)
        root.mainloop()

    def developerDetection(self) -> None:
        """
        Provide for developer to use
        """
        self.other_root = Toplevel(self.root)
        self.other_root.resizable(False, False)
        self.other_root.title('Developer check')
        self.other_root.geometry("500x200+700+300")
        Label(self.other_root, text='Please enter password:', font=('华文新魏', 18)).place(relx=0.26, rely=0.15)
        self.password = Entry(self.other_root, width=25, font=('仿宋', 18), show='*')
        self.password.focus_set()
        self.password.place(relx=0.20, rely=0.35)
        b1 = Button(self.other_root, text='OK', command=self.developerOption, font=('华文新魏', 18), relief=RAISED, overrelief="sunken", width=6, height=1)
        b1.place(relx=0.62, rely=0.7)
        b2 = Button(self.other_root, text='CANCEL', command=lambda: self.other_root.destroy(), font=('华文新魏', 18), relief=RAISED, overrelief="sunken", width=6, height=1)
        b2.place(relx=0.2, rely=0.7)
        b1.bind_all('<Return>', self.developerOptionPro)

    def developerOptionPro(self, _event) -> None:
        """
        Enter event
        """
        self.developerOption()

    def developerOption(self) -> None:
        """
        Provide for developer to use
        """
        try:
            _password = str(self.password.get())
            self.password = None
            self.other_root.destroy()
            self.other_root = None
        except _tkinter.TclError:
            _password = ""
            pass
        except AttributeError:
            return
        root = Toplevel(self.root)
        root.resizable(False, False)
        if _password == str(developer_password):
            root.title("Devoloper Option")
            root.geometry("800x500+550+185")
            Button(root, text='Manage of edition', command=self.EditionManage, font=('华文新魏', 19),
                   relief=RAISED, overrelief="sunken", width=15, height=2).place(relx=0.37, rely=0.15)
            Button(root, text='Manage of agent', command=self.agentManage, font=('华文新魏', 19), relief=RAISED, width=15,
                   overrelief="sunken", height=2).place(relx=0.37, rely=0.4)
            Button(root, text='All status', command=lambda: self.show_all_status(root), font=('华文新魏', 19), relief=RAISED, width=15,
                   overrelief="sunken", height=2).place(relx=0.37, rely=0.65)
            Button(root, text='Achieve', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
                   overrelief="sunken", height=2).place(relx=0.80, rely=0.85)
            root.mainloop()
        else:
            root.title("Tips")
            root.geometry("400x200+750+350")
            Label(root, text='Developer Option', font=('华文新魏', 24), justify=LEFT).place(relx=0.23, rely=0.1)
            b = Button(root, text='退出', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=12, overrelief="sunken", height=2)
            b.place(relx=0.33, rely=0.60)

    def EditionManage(self) -> None:
        """
        Use for manage edition
        """
        root = Toplevel(self.root)
        root.resizable(False, False)
        root.title('Manage edition')
        root.geometry("600x400+655+225")
        edition_dict = requests.post(post_edition_url, data={"edition": self.edition}).json()
        current_edition = self.edition
        latest_edition = edition_dict.get("edition")
        Label(root, text=f'Current edition:{current_edition}\n\nLatest edition:{latest_edition}', font=('华文新魏', 16), justify=CENTER).place(
            relx=0.36,
            rely=0.1)
        img_open = imim.open("project\\fm.jpg")
        img_png = ImageTk.PhotoImage(img_open)
        Label(root, text=f'Set current edition:', font=('华文新魏', 19), justify=CENTER).place(relx=0.18, rely=0.35, height=40)
        setting_current_edition = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER)
        setting_current_edition.place(relx=0.53, rely=0.35, width=80, height=40)
        Button(root, image=img_png, command=lambda: self.setCurrentEdition(root, setting_current_edition),
               relief=RAISED, overrelief="sunken").place(relx=0.68, rely=0.34)
        Label(root, text=f' Set  latest  edition:', font=('华文新魏', 19), justify=CENTER).place(relx=0.18, rely=0.5, height=40)
        setting_edition = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER)
        setting_edition.place(relx=0.53, rely=0.5, width=80, height=40)
        Button(root, image=img_png, command=lambda: self.setLatestEdition(root, setting_current_edition),
               relief=RAISED, overrelief="sunken").place(relx=0.68, rely=0.5, height=40)
        Button(root, text='Update ++0.01', command=lambda: self.updateEdition(root), font=('华文新魏', 19), relief=RAISED, width=12,
               overrelief="sunken", height=2).place(relx=0.35, rely=0.7)
        Button(root, text='Achieve', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=10,
               overrelief="sunken", height=2).place(relx=0.75, rely=0.80)
        root.mainloop()


    def setLatestEdition(self, parent_root: Toplevel, edition: Entry) -> None:
        """
        Use for set edition
        """
        result = requests.post(set_edition_url, data={"edition": edition.get()}).json()
        root = Toplevel(parent_root)
        root.resizable(False, False)
        if result.get('result'):
            root.title("Tips")
            root.geometry("400x200+750+350")
            Label(root, text=result.get("message", "?????"), font=('华文新魏', 12), justify=LEFT).place(relx=0.23, rely=0.1)
            b = Button(root, text='Return', command=parent_root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
                       overrelief="sunken", height=2)
            b.place(relx=0.33, rely=0.60)
        else:
            root.destroy()
            self.tipsWiondow(root=parent_root, words="The format of the version number entered is incorrect", size='small')


    def setCurrentEdition(self, parent_root: Toplevel, edition: Entry) -> None:
        """
        Use for set edition
        """
        root = Toplevel(parent_root)
        root.resizable(False, False)
        try:
            edition = float(edition.get())
            with open('project/Collect/src/edition.py', 'r', encoding='utf-8') as f:
                old_str = f.read()
            new_str = old_str.replace(f'edition = "{self.edition}"', f'edition = "{edition}"')
            with open('project/Collect/src/edition.py', 'w', encoding='utf-8') as f:
                f.write(new_str)
            root.title("Tips")
            root.geometry("400x200+750+350")
            Label(root, text=f"Update successful,current edition:{edition}", font=('华文新魏', 12), justify=LEFT).place(relx=0.23, rely=0.1)
            b = Button(root, text='Exit', command=self.root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
                       overrelief="sunken", height=2)
            b.place(relx=0.33, rely=0.60)
        except ValueError:
            root.destroy()
            self.tipsWiondow(root=parent_root, words="The format of the version number entered is incorrect", size='small')

    @staticmethod
    def updateEdition(parent_root: Toplevel) -> None:
        """
        Use for update edition
        """
        result = requests.get(update_edition_url).json()
        root = Toplevel(parent_root)
        root.resizable(False, False)
        if result.get('result'):
            root.title("Tips")
            root.geometry("400x200+750+350")
            Label(root, text=result.get("message", "?????"), font=('华文新魏', 12), justify=LEFT).place(relx=0.23, rely=0.1)
            b = Button(root, text='Return', command=parent_root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
                       overrelief="sunken", height=2)
            b.place(relx=0.33, rely=0.60)
        else:
            root.title("Tips")
            root.geometry("400x200+750+350")
            Label(root, text=result.get("message", "?????"), font=('华文新魏', 12), justify=LEFT).place(relx=0.23, rely=0.1)
            b = Button(root, text='Return', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
                       overrelief="sunken", height=2)
            b.place(relx=0.33, rely=0.60)

    def show_all_status(self, parent_root) -> None:
        """
        Show and modify running status of all machine code
        """
        root = Toplevel(parent_root)
        root.resizable(False, False)
        root.title("Status")
        root.geometry("400x200+750+350")
        self.tipsWiondow(root, "NULL", size="small")

    def agentManage(self) -> None:
        """
        Use for manage tunnel agent
        """
        root = Toplevel(self.root)
        root.resizable(False, False)
        root.title('Manage agent')
        root.geometry("600x400+655+225")
        Button(root, text='Show configuration', command=lambda: self.showAgentConfiguration(root), font=('华文新魏', 16),
               relief=RAISED, overrelief="sunken", width=12, height=1).place(relx=0.1, rely=0.2, width=200, height=50)
        Button(root, text='Set configuration', command=lambda: self.setAgentConfiguration(root), font=('华文新魏', 16),
               relief=RAISED, overrelief="sunken", width=12, height=1).place(relx=0.1, rely=0.5, width=200, height=50)
        Button(root, text='Show information', command=lambda: self.showAgentInformation(root), font=('华文新魏', 16),
               relief=RAISED, overrelief="sunken", width=12, height=1).place(relx=0.5, rely=0.2, width=200, height=50)
        Button(root, text='Set information', command=lambda: self.setAgentInformation(root), font=('华文新魏', 16),
               relief=RAISED, overrelief="sunken", width=12, height=1).place(relx=0.5, rely=0.5, width=200, height=50)
        Button(root, text='完成', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=10,
               overrelief="sunken", height=2).place(relx=0.75, rely=0.80)
        root.mainloop()

    @staticmethod
    def showAgentConfiguration(parent_root: Toplevel):
        """
        Show the condition of tunnel agent configuration
        """
        root = Toplevel(parent_root)
        root.resizable(False, False)
        root.title("Show configuration")
        _res = requests.get(get_agent_configuration).json()
        configuration = _res.get("data")
        machine_code = list(configuration.keys())
        tunnel_agent = list(configuration.values())
        length = len(machine_code)
        text_list = [f'<{machine_code[i]}>' + "   USE   " + f'[{tunnel_agent[i]}]' for i in range(length)]
        root.geometry(f"500x420+700+250")
        text = Text(root, font=('华文新魏', 15), width=45, height=19)
        text.place(relx=0.03, rely=0.01)
        scroll = Scrollbar(root, bd=30, relief=FLAT, width=25)
        scroll.pack(side=RIGHT, fill=Y)
        scroll.config(command=text.yview)
        text.config(yscrollcommand=scroll.set)
        for each in text_list:
            text.insert(END, each)
            text.insert(END, "\n\n")
        text.config(state="disabled")

    def setAgentConfiguration(self, parent_root: Toplevel):
        """
        Set the condition of tunnel agent configuration
        """
        root = Toplevel(parent_root)
        root.resizable(False, False)
        root.title("Set configuration")
        root.geometry("550x450+670+240")
        Label(root, text="Enter machine code", font=('华文新魏', 19), justify=LEFT, fg="red").place(relx=0.05, rely=0.1)
        machine_code_entry = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER)
        machine_code_entry.place(relx=0.5, rely=0.1, width=260, height=35)
        Label(root, text="Enter tunnel name", font=('华文新魏', 19), justify=LEFT).place(relx=0.05, rely=0.25)
        tunnel_name_entry = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER)
        tunnel_name_entry.place(relx=0.5, rely=0.25, width=260, height=35)
        Button(root, text='Save', command=lambda: self.saveAgentConfiguration(root, machine_code_entry, tunnel_name_entry), font=('华文新魏', 16),
               relief=RAISED, overrelief="sunken", width=12, height=1).place(relx=0.4, rely=0.35, width=100, height=50)
        Label(root, text="Enter machine code\n(You want deleted)", font=('华文新魏', 19), justify=CENTER).place(relx=0.05, rely=0.5)
        delete_machine_code_entry = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER)
        delete_machine_code_entry.place(relx=0.5, rely=0.52, width=260, height=35)
        Button(root, text='Delete', command=lambda: self.deleteAgentConfiguration(root, delete_machine_code_entry), font=('华文新魏', 16),
               relief=RAISED, overrelief="sunken", width=12, height=1).place(relx=0.4, rely=0.65, width=100, height=50)
        Button(root, text='Achieve', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=10,
               overrelief="sunken", height=2).place(relx=0.75, rely=0.80)

    def saveAgentConfiguration(self, parent_root: Toplevel, machine_code_entry: Entry, tunnel_name_entry: Entry) -> None:
        """
        Save agent configuration setting
        """
        _machine_code = machine_code_entry.get()
        _tunnel_name = tunnel_name_entry.get()
        _data = {"machine_code": _machine_code, "tunnel_name": _tunnel_name}
        _response = requests.post(set_agent_configuration, data=_data).json()
        if _response.get("result"):
            self.tipsWiondow(parent_root, _response.get("message"), size="small")
            tunnel_name_entry.delete(0, 'end')
            machine_code_entry.delete(0, 'end')
        else:
            self.tipsWiondow(parent_root, _response.get("message"), size="small")

    def deleteAgentConfiguration(self, parent_root: Toplevel, delete_machine_code_entry: Entry) -> None:
        """
        Delete agent configuration setting
        """
        _delete_machine_code = delete_machine_code_entry.get()
        _data = {"machine_code": _delete_machine_code}
        _response = requests.post(delete_agent_configuration, data=_data).json()
        if _response.get("result"):
            self.tipsWiondow(parent_root, _response.get("message"), size="small")
            delete_machine_code_entry.delete(0, 'end')
        else:
            self.tipsWiondow(parent_root, _response.get("message"), size="small")

    @staticmethod
    def showAgentInformation(parent_root: Toplevel):
        """
        Show the condition of tunnel agent configuration
        """
        root = Toplevel(parent_root)
        root.resizable(False, False)
        root.title("Show information")
        root.geometry(f"500x420+700+250")
        _res = requests.get(get_agent_information).json()
        information = _res.get("data")
        text = Text(root, font=('华文新魏', 15), width=45, height=19)
        text.place(relx=0.03, rely=0.01)
        scroll = Scrollbar(root, bd=30, relief=FLAT, width=25)
        scroll.pack(side=RIGHT, fill=Y)
        scroll.config(command=text.yview)
        text.config(yscrollcommand=scroll.set)
        for _tunnel_name in information.keys():
            detail = information.get(_tunnel_name)
            _words = f"{_tunnel_name}:\n\n    address  :  {detail.get('address')}\n\n    user_name  :  {detail.get('user_name')}\n\n    password  :  {detail.get('password')}\n\n    request_frequency  :  {detail.get('request_frequency')}\n\n"
            text.insert(END, _words)
        text.config(state="disabled")

    def setAgentInformation(self, parent_root: Toplevel):
        """
        Set the condition of tunnel agent information
        """
        root = Toplevel(parent_root)
        root.resizable(False, False)
        root.title("Set information")
        root.geometry("600x580+670+240")
        Label(root, text="Enter tunnel name", font=('华文新魏', 19), justify=LEFT, fg="red").place(relx=0.07, rely=0.1)
        tunnel_name_entry = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER, fg="red")
        tunnel_name_entry.place(relx=0.48, rely=0.1, width=260, height=35)
        Label(root, text="Enter address", font=('华文新魏', 19), justify=LEFT).place(relx=0.07, rely=0.2)
        address_entry = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER)
        address_entry.place(relx=0.48, rely=0.2, width=260, height=35)
        Label(root, text="Enter user name", font=('华文新魏', 19), justify=LEFT).place(relx=0.07, rely=0.3)
        user_name_entry = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER)
        user_name_entry.place(relx=0.48, rely=0.3, width=260, height=35)
        Label(root, text="Enter password", font=('华文新魏', 19), justify=LEFT).place(relx=0.07, rely=0.4)
        password_entry = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER)
        password_entry.place(relx=0.48, rely=0.4, width=260, height=35)
        Label(root, text="Enter frequency", font=('华文新魏', 19), justify=LEFT).place(relx=0.07, rely=0.5)
        request_frequency_entry = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER)
        request_frequency_entry.place(relx=0.48, rely=0.5, width=260, height=35)
        Button(root, text='Save', command=lambda: self.saveAgentInformation(root, tunnel_name_entry, address_entry, user_name_entry, password_entry, request_frequency_entry), font=('华文新魏', 16),
               relief=RAISED, overrelief="sunken", width=12, height=1).place(relx=0.4, rely=0.59, width=100, height=50)
        Label(root, text="Enter tunnel name\n(You want deleted)", font=('华文新魏', 19), justify=CENTER).place(relx=0.05, rely=0.69)
        delete_tunnel_name_entry = Entry(root, width=10, font=('华文新魏', 19), justify=CENTER)
        delete_tunnel_name_entry.place(relx=0.5, rely=0.71, width=260, height=35)
        Button(root, text='Delete', command=lambda: self.deleteAgentInformation(root, delete_tunnel_name_entry), font=('华文新魏', 16),
               relief=RAISED, overrelief="sunken", width=12, height=1).place(relx=0.4, rely=0.8, width=100, height=50)
        Button(root, text='Achieve', command=root.destroy, font=('华文新魏', 15), relief=RAISED, width=10,
               overrelief="sunken", height=2).place(relx=0.75, rely=0.85)

    def saveAgentInformation(self, parent_root: Toplevel, tunnel_name_entry: Entry, address_entry: Entry, user_name_entry: Entry, password_entry: Entry, request_frequency_entry: Entry) -> None:
        """
        Save agent information setting
        """
        _tunnel_name = tunnel_name_entry.get()
        if not _tunnel_name:
            self.tipsWiondow(parent_root, 'ERROR: Tunnel name cannot be empty', size="small")
            return
        _address = address_entry.get() if tunnel_name_entry.get() else None
        _user_name = user_name_entry.get() if tunnel_name_entry.get() else None
        _password = password_entry.get() if tunnel_name_entry.get() else None
        try:
            _request_frequency = int(request_frequency_entry.get())
        except ValueError:
            self.tipsWiondow(parent_root, "ERROR: Request frequency must is type of Int" + "\n\n" + traceback.format_exc())
            return
        _data = {"tunnel_name": _tunnel_name, "address": _address, "user_name": _user_name, "password": _password, "request_frequency": _request_frequency}
        _response = requests.post(set_anget_information, data=_data).json()
        if _response.get("result"):
            self.tipsWiondow(parent_root, _response.get("message"), size="small")
            tunnel_name_entry.delete(0, 'end')
            address_entry.delete(0, 'end')
            user_name_entry.delete(0, 'end')
            password_entry.delete(0, 'end')
            request_frequency_entry.delete(0, 'end')
        else:
            self.tipsWiondow(parent_root, _response.get("message"), size="small")

    def deleteAgentInformation(self, parent_root: Toplevel, delete_tunnel_name_entry: Entry) -> None:
        """
        Delete agent information
        """
        delete_tunnel_name = delete_tunnel_name_entry.get()
        _data = {"tunnel_name": delete_tunnel_name}
        _response = requests.post(delete_agent_information, data=_data).json()
        if _response.get("result"):
            self.tipsWiondow(parent_root, _response.get("message"), size="small")
            delete_tunnel_name_entry.delete(0, 'end')
        else:
            self.tipsWiondow(parent_root, _response.get("message"), size="small")

    @staticmethod
    def close(self_root, root) -> None:
        """
        Quit application
        """
        self_root.destroy()
        root.destroy()

    def main(self) -> None:
        """
        Main method
        """
        Label(self.root, text='1、初次使用先点击左上角按钮\n\n2、设置完成后直接运行即可', font=('华文新魏', 16), justify=LEFT).place(
            relx=0.35,
            rely=0.1)
        Button(self.root, text='初次使用点这里', command=self.build, font=('华文新魏', 14),
               relief=RAISED, overrelief="sunken", height=2, width=13).place(relx=0.03, rely=0.03)
        Button(self.root, text='设置', command=self.setting, font=('华文新魏', 16),
               relief=RAISED, overrelief="sunken", height=2, width=12).place(relx=0.8, rely=0.03)
        Button(self.root, text='开始爬取', command=self.run_crawl, font=('华文新魏', 25),
               relief=RAISED, overrelief="sunken", height=2, width=12, fg='pink', bg='grey').place(relx=0.38, rely=0.30)
        Button(self.root, text='开始保存', command=self.run_save, font=('华文新魏', 25),
               relief=RAISED, overrelief="sunken", height=2, width=12, fg='black', bg='grey').place(relx=0.38, rely=0.55)
        Button(self.root, text='退出', command=self.root.destroy, font=('华文新魏', 15), relief=RAISED, width=12,
               overrelief="sunken", height=2).place(relx=0.80, rely=0.85)
        Button(self.root, text='查看', command=self.show_setting, font=('华文新魏', 15), relief=RAISED, width=15,
               overrelief="sunken", height=2).place(relx=0.02, rely=0.85)
        Button(self.root, text='开发者选项', command=self.developerDetection, font=('华文新魏', 16),
               relief=RAISED, overrelief="sunken", height=2, width=10, fg='black', bg='green').place(relx=0.02, rely=0.73)
        self.root.mainloop()


if __name__ == '__main__':
    try:
        App().main()
    except Exception:
        eg.msgbox(title='错误', msg=traceback.format_exc())
