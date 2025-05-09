import sys
sys.path.append('....')
import os
import sys
import logging
from xinwei.project.Collect.src.multiprocessloghandler import MultiprocessHandler



def logger_define(dir_path, plat_name):
    # error日志路径
    error_dir = os.path.join(dir_path, "error/{}/".format(plat_name))
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)

    # info日志路径
    info_dir = os.path.join(dir_path, "info/{}/".format(plat_name))
    if not os.path.exists(info_dir):
        os.makedirs(info_dir)

    # info日志文件，error日志文件
    info_file = info_dir + "{}.log".format(plat_name)
    error_file = error_dir + "{}.log".format(plat_name)

    # 生成logger
    log = logging.getLogger("{}".format(plat_name))
    log.setLevel("INFO")

    # 定义日志输出格式
    formattler = '%(asctime)s|%(processName)s|%(threadName)s|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s'
    fmt = logging.Formatter(formattler)

    # 设置日志控制台输出
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)

    # 设置控制台文件输出
    log_handler_info = MultiprocessHandler(info_file)
    log_handler_err = MultiprocessHandler(error_file)

    # 设置日志输出格式：
    stream_handler.setFormatter(fmt)
    log_handler_info.setFormatter(fmt)
    log_handler_err.setFormatter(fmt)

    # 设置过滤条件
    info_filter = logging.Filter()
    info_filter.filter = lambda record: record.levelno < logging.WARNING  # 设置过滤等级
    err_filter = logging.Filter()
    err_filter.filter = lambda record: record.levelno >= logging.WARNING

    # 对文件输出日志添加过滤条件
    log_handler_info.addFilter(info_filter)
    log_handler_err.addFilter(err_filter)

    # 对logger增加handler日志处理器
    log.addHandler(log_handler_info)
    log.addHandler(log_handler_err)
    log.addHandler(stream_handler)

    return log


# if __name__ == '__main__':
    # logger = logger_define(os.getcwd(), "laowang")
    # a = [1, 2, 0, 4, 6, 0, 9]
    # for i in a:
    #     try:
    #         b = 3 / i
    #         logger.info('b的值为:{}'.format(b))
    #     except Exception as e:
    #         logger.error(traceback.format_exc())
    #         continue
