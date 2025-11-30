#  coding: utf-8
#
#  Copyright (C) 2022-2024, Inc. All Rights Reserved
#
#  @Time    : 2024/11/15 10:44
#  @Author  : yan que
#  @Email   : yanquer@qq.com
#  @File    : logger.py
#  @Project : mytest

import inspect
import logging
from logging.handlers import RotatingFileHandler
from typing import Type, Dict

# logging.basicConfig(level=logging.INFO)

ALL="[ALL]"


# 获取调用者的 __name__
def get_caller_name():
    # 获取当前栈帧
    frame = inspect.currentframe()
    try:
        # 获取调用者的栈帧 (此处封装有额外的两层此文件的调用, 所以多找两层, 不然找到的是 common.logger 自己)
        caller_frame = frame.f_back.f_back.f_back
        # 获取调用者的上下文
        caller_name = caller_frame.f_globals["__name__"]
        return caller_name
    except AttributeError:
        return ALL
    finally:
        del frame  # 清理引用以防止循环引用


# GLOBAL_LOGGER = logging.getLogger(ALL)


# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class LoggerEvery(object):
    DEFAULT_LOG_LEVEL = logging.DEBUG
    DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    DEFAULT_LOG_FILE = "log/run.log"

    @classmethod
    def add_handler_format(cls, handler: logging.Handler) -> None:
        # 设置日志格式
        formatter = logging.Formatter(
            fmt=cls.DEFAULT_LOG_FORMAT,
            datefmt=cls.DEFAULT_LOG_DATE_FORMAT,
        )
        handler.setFormatter(formatter)

    @classmethod
    def add_console_handler(cls, logger: logging.Logger, level: int | None = None):
        console_handler = logging.StreamHandler()
        if level is not None:
            console_handler.setLevel(level)
        # 设置日志格式
        cls.add_handler_format(console_handler)
        logger.addHandler(console_handler)

    @classmethod
    def add_file_handler(cls, logger: logging.Logger, file_name: str | None=DEFAULT_LOG_FILE, level: int | None = None):
        file_handler = logging.FileHandler(file_name or cls.DEFAULT_LOG_FILE)
        if level is not None:
            file_handler.setLevel(level)
        # 设置日志格式
        cls.add_handler_format(file_handler)
        logger.addHandler(file_handler)

    @classmethod
    def add_rotating_log_handler(cls, logger: logging.Logger, file_name: str | None=DEFAULT_LOG_FILE, level: int | None = None):
        # 创建 RotatingFileHandler，设置最大文件大小为 10MB，最多保留 15 个备份文件
        rotating_handler = RotatingFileHandler(file_name or cls.DEFAULT_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=15)
        if level is not None:
            rotating_handler.setLevel(level)

        # 设置日志格式
        cls.add_handler_format(rotating_handler)

        # 添加 handler 到 logger
        logger.addHandler(rotating_handler)

    @staticmethod
    def add_all_logger_handler(logger: logging.Logger, level: int | None = None):
        LoggerEvery.add_console_handler(logger, level)
        LoggerEvery.add_file_handler(logger, None, level)


if __name__ == '__main__':
    LoggerEvery.add_console_handler(_LOGGER)
    _LOGGER.debug('debug - Hello World')
    _LOGGER.info('info - Hello World')
    _LOGGER.warning('warn - Hello World')








