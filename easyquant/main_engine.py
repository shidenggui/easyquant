import importlib
import os
import sys
from collections import OrderedDict

import easytrader
from logbook import Logger, StreamHandler

from .clock_engine import *
from .event_engine import *
from .event_type import EventType
from .quotation_engine import *

log = Logger(os.path.basename(__file__))
StreamHandler(sys.stdout).push_application()

PY_VERSION = sys.version_info[:2]
if PY_VERSION < (3, 5):
    raise Exception('Python 版本需要 3.5 或以上, 当前版本为 %s.%s 请升级 Python' % PY_VERSION)


class MainEngine:
    """主引擎，负责行情 / 事件驱动引擎 / 交易"""

    def __init__(self, broker, need_data='me.json'):
        """初始化事件 / 行情 引擎并启动事件引擎
        """
        self.user = easytrader.use(broker)
        self.user.prepare(need_data)

        self.event_engine = EventEngine()
        self.quotation_engine = Quotation(self.event_engine)
        self.clock_engine = ClockEngine(self.event_engine)

        self.event_engine.register(EventType.TIMER, self.second_click)

        # 保存读取的策略类
        self.strategies = OrderedDict()
        self.strategy_list = list()

        print('启动主引擎')

    def second_click(self, event):
        pass

    def start(self):
        """启动主引擎"""
        self.event_engine.start()
        self.quotation_engine.start()
        self.clock_engine.start()

    def load_strategy(self):
        """动态加载策略"""
        s_folder = 'strategies'
        strategies = os.listdir(s_folder)
        strategies = filter(lambda file: file.endswith('.py') and file != '__init__.py', strategies)
        importlib.import_module(s_folder)
        for strategy_file in strategies:
            strategy_module_name = os.path.basename(strategy_file)[:-3]
            log.info('加载策略: %s' % strategy_module_name)
            strategy_module = importlib.import_module('.' + strategy_module_name, 'strategies')
            self.strategy_list.append(getattr(strategy_module, 'Strategy')(self.user))
        for strategy in self.strategy_list:
            self.event_engine.register(EventType.QUOTATION, strategy.run)
            self.event_engine.register(EventType.CLOCK, strategy.clock)
        log.info('加载策略完毕')
