# coding: utf-8
import datetime
import time
from threading import Thread
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
from logsys import LogSys

class Engine(object):
    def __init__(self):
        pass

    def log_instance(self, logtype, filename, loglevel='DEBUG'):
        """
        生成log实例的接口
        :logtype: <stream, file>
        :filename: 需要打印log的文件名
        :loglevel: <DEBUG, INFO, CRITICAL, ERROR, WARNING, NOTICE>
        """
        return LogSys(logtype, filename, loglevel)
