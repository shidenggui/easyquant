# !/usr/bin/python
# vim: set fileencoding=utf8 :
#
__author__ = 'keping.chu'

import importlib
import os
from threading import Thread, Lock

import time
from easyquant.log_handler.default_handler import DefaultLogHandler
from easyquant.main_engine import MainEngine
from easyquant.multiprocess.strategy_wrapper import ProcessWrapper
from easyquant.push_engine.clock_engine import ClockEngine
from .fixeddataengine import FixedDataEngine


class FixedMainEngine(MainEngine):
    def __init__(self, broker, need_data='ht.json', quotation_engines=[FixedDataEngine],
                 log_handler=DefaultLogHandler(), ext_stocks=[]):
        super(FixedMainEngine, self).__init__(broker, need_data, [], log_handler)
        if type(quotation_engines) != list:
            quotation_engines = [quotation_engines]
        self.quotation_engines = []
        # 修改时间缓存
        self._cache = {}
        # 文件进程映射
        self._process_map = {}
        # 文件模块映射
        self._modules = {}
        self._names = None
        # 加载锁
        self.lock = Lock()
        # 加载线程
        self._watch_thread = Thread(target=self._load_strategy)
        positions = [p['stock_code'] for p in self.user.position]
        positions.extend(ext_stocks)
        for quotation_engine in quotation_engines:
            self.quotation_engines.append(quotation_engine(self.event_engine, self.clock_engine, positions))

    def load(self, names, strategy_file):
        with self.lock:
            mtime = os.path.getmtime(os.path.join('strategies', strategy_file))

            # 是否需要重新加载
            reload = False
            strategy_module_name = os.path.basename(strategy_file)[:-3]
            if self._cache.get(strategy_file, None) == mtime:
                return
            elif self._cache.get(strategy_file, None) is not None:
                # 原有进程退出
                _process = self._process_map.get(strategy_file)
                self.unbind_event(_process)
                _process.stop()
                self.log.info(u'卸载策略: %s' % strategy_module_name)
                time.sleep(2)
                reload = True
            # 重新加载
            if reload:
                strategy_module = importlib.reload(self._modules[strategy_file])
            else:
                strategy_module = importlib.import_module('.' + strategy_module_name, 'strategies')
            self._modules[strategy_file] = strategy_module

            strategy_class = getattr(strategy_module, 'Strategy')
            if names is None or strategy_class.name in names:
                self.strategies[strategy_module_name] = strategy_class
                # 进程包装
                _process = ProcessWrapper(strategy_class(self.user, log_handler=self.log, main_engine=self))
                # 缓存加载信息
                self._process_map[strategy_file] = _process
                self.strategy_list.append(_process)
                self._cache[strategy_file] = mtime
                self.bind_event(_process)
                self.log.info(u'加载策略: %s' % strategy_module_name)

    def bind_event(self, strategy):
        """
        绑定事件
        """
        for quotation_engine in self.quotation_engines:
            self.event_engine.register(quotation_engine.EventType, strategy.on_event)
        self.event_engine.register(ClockEngine.EventType, strategy.on_clock)

    def unbind_event(self, strategy):
        """
        移除事件
        """
        for quotation_engine in self.quotation_engines:
            self.event_engine.unregister(quotation_engine.EventType, strategy.on_event)
        self.event_engine.unregister(ClockEngine.EventType, strategy.on_clock)

    def load_strategy(self, names=None):
        """动态加载策略
        :param names: 策略名列表，元素为策略的 name 属性"""
        s_folder = 'strategies'
        self._names = names
        strategies = os.listdir(s_folder)
        strategies = filter(lambda file: file.endswith('.py') and file != '__init__.py', strategies)
        importlib.import_module(s_folder)
        for strategy_file in strategies:
            self.load(self._names, strategy_file)
        # 如果线程没有启动，就启动策略监视线程
        if not self._watch_thread.is_alive():
            self._watch_thread.start()

    def _load_strategy(self):
        while True:
            try:
                self.load_strategy(self._names)
                time.sleep(2)
            except Exception as e:
                print(e)
