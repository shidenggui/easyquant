# !/usr/bin/python
# vim: set fileencoding=utf8 :
#
__author__ = 'keping.chu'

from easyquant.main_engine import MainEngine
from easyquant.log_handler.default_handler import DefaultLogHandler
from .fixeddataengine import FixedDataEngine
from easyquant.push_engine.clock_engine import ClockEngine
import os
import importlib

from easyquant.multiprocess.strategy_wrapper import ProcessWrapper


class FixedMainEngine(MainEngine):

    def __init__(self, broker, need_data='ht.json', quotation_engines=[FixedDataEngine],
                 log_handler=DefaultLogHandler(), ext_stocks=[]):
        super(FixedMainEngine, self).__init__(broker, need_data, [], log_handler)
        if type(quotation_engines) != list:
            quotation_engines = [quotation_engines]
        self.quotation_engines = []
        positions = [p['stock_code'] for p in self.user.position]
        positions.extend(ext_stocks)
        for quotation_engine in quotation_engines:
            self.quotation_engines.append(quotation_engine(self.event_engine, positions))

    def load_strategy(self, names=None):
        """动态加载策略
        :param names: 策略名列表，元素为策略的 name 属性"""
        s_folder = 'strategies'
        strategies = os.listdir(s_folder)
        strategies = filter(lambda file: file.endswith('.py') and file != '__init__.py', strategies)
        importlib.import_module(s_folder)
        for strategy_file in strategies:
            strategy_module_name = os.path.basename(strategy_file)[:-3]
            strategy_module = importlib.import_module('.' + strategy_module_name, 'strategies')
            strategy_class = getattr(strategy_module, 'Strategy')

            if names is None or strategy_class.name in names:
                self.strategies[strategy_module_name] = strategy_class
                self.strategy_list.append(ProcessWrapper(strategy_class(self.user, log_handler=self.log, main_engine=self)))
                self.log.info(u'加载策略: %s' % strategy_module_name)
        for strategy in self.strategy_list:
            for quotation_engine in self.quotation_engines:
                self.event_engine.register(quotation_engine.EventType, strategy.on_event)
            self.event_engine.register(ClockEngine.EventType, strategy.on_clock)
        self.log.info(u'加载策略完毕')