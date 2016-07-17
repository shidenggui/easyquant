import importlib
import os
import pathlib
import sys
import time
from collections import OrderedDict
import dill

import easytrader
from logbook import Logger, StreamHandler

from .event_engine import EventEngine
from .log_handler.default_handler import DefaultLogHandler
from .push_engine.clock_engine import ClockEngine
from .push_engine.quotation_engine import DefaultQuotationEngine

log = Logger(os.path.basename(__file__))
StreamHandler(sys.stdout).push_application()

PY_MAJOR_VERSION, PY_MINOR_VERSION = sys.version_info[:2]
if (PY_MAJOR_VERSION, PY_MINOR_VERSION) < (3, 5):
    raise Exception('Python 版本需要 3.5 或以上, 当前版本为 %s.%s 请升级 Python' % (PY_MAJOR_VERSION, PY_MINOR_VERSION))

ACCOUNT_OBJECT_FILE = 'account.session'

class MainEngine:
    """主引擎，负责行情 / 事件驱动引擎 / 交易"""

    def __init__(self, broker=None, need_data=None, quotation_engines=None,
                 log_handler=DefaultLogHandler(), tzinfo=None):
        """初始化事件 / 行情 引擎并启动事件引擎
        """
        self.log = log_handler

        # 登录账户
        if (broker is not None) and (need_data is not None):
            self.user = easytrader.use(broker)
            need_data_file = pathlib.Path(need_data)
            if need_data_file.exists():
                self.user.prepare(need_data)
                with open(ACCOUNT_OBJECT_FILE, 'wb') as f:
                    dill.dump(self.user, f)
            else:
                log_handler.warn("券商账号信息文件 %s 不存在, easytrader 将不可用" % need_data)
        else:
            self.user = None
            self.log.info('选择了无交易模式')

        self.event_engine = EventEngine()
        self.clock_engine = ClockEngine(self.event_engine, tzinfo)

        quotation_engines = quotation_engines or [DefaultQuotationEngine]

        if type(quotation_engines) != list:
            quotation_engines = [quotation_engines]
        self.quotation_engines = []
        for quotation_engine in quotation_engines:
            self.quotation_engines.append(quotation_engine(self.event_engine, self.clock_engine))

        # 保存读取的策略类
        self.strategies = OrderedDict()
        self.strategy_list = list()

        self.log.info('启动主引擎')

    def start(self):
        """启动主引擎"""
        self.event_engine.start()
        time.sleep(10)
        for quotation_engine in self.quotation_engines:
            quotation_engine.start()
        self.clock_engine.start()

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
                self.strategy_list.append(strategy_class(log_handler=self.log, main_engine=self))
                self.log.info('加载策略: %s' % strategy_module_name)
        for strategy in self.strategy_list:
            self.event_engine.register(ClockEngine.EventType, strategy.clock)
            for quotation_engine in self.quotation_engines:
                self.event_engine.register(quotation_engine.EventType, strategy.run)
        self.log.info('加载策略完毕')
