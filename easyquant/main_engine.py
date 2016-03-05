import importlib
import os
import sys
from collections import OrderedDict

import easytrader
from logbook import Logger, StreamHandler

from .event_engine import EventEngine
from .push_engine.clock_engine import ClockEngine
from .push_engine.quotation_engine import DefaultQuotationEngine

log = Logger(os.path.basename(__file__))
StreamHandler(sys.stdout).push_application()

PY_VERSION = sys.version_info[:2]
if PY_VERSION < (3, 5):
    raise Exception('Python 版本需要 3.5 或以上, 当前版本为 %s.%s 请升级 Python' % PY_VERSION)


class MainEngine:
    """主引擎，负责行情 / 事件驱动引擎 / 交易"""

    def __init__(self, broker, need_data='me.json', quotation_engines=[DefaultQuotationEngine], log_handler=log):
        """初始化事件 / 行情 引擎并启动事件引擎
        """
        # 登录账户
        self.user = easytrader.use(broker)
        self.user.prepare(need_data)

        self.event_engine = EventEngine()
        self.clock_engine = ClockEngine(self.event_engine)

        if type(quotation_engines) != list:
            quotation_engines = [quotation_engines]
        self.quotation_engines = []
        for quotation_engine in quotation_engines:
            self.quotation_engines.append(quotation_engine(self.event_engine))

        # 保存读取的策略类
        self.strategies = OrderedDict()
        self.strategy_list = list()
        self.log = log_handler

        self.log.info('启动主引擎')

    def start(self):
        """启动主引擎"""
        self.event_engine.start()
        for quotation_engine in self.quotation_engines:
            quotation_engine.start()
        self.clock_engine.start()

    def load_strategy(self):
        """动态加载策略"""
        s_folder = 'strategies'
        strategies = os.listdir(s_folder)
        strategies = filter(lambda file: file.endswith('.py') and file != '__init__.py', strategies)
        importlib.import_module(s_folder)
        for strategy_file in strategies:
            strategy_module_name = os.path.basename(strategy_file)[:-3]
            strategy_module = importlib.import_module('.' + strategy_module_name, 'strategies')
            strategy_class = getattr(strategy_module, 'Strategy')

            self.strategies[strategy_module_name] = strategy_class
            self.strategy_list.append(strategy_class(self.user))
            self.log.info('加载策略: %s' % strategy_module_name)
        for strategy in self.strategy_list:
            for quotation_engine in self.quotation_engines:
                self.event_engine.register(quotation_engine.EventType, strategy.run)
            self.event_engine.register(ClockEngine.EventType, strategy.clock)
        self.log.info('加载策略完毕')
