import os
import sys
import importlib
from collections import OrderedDict
from logbook import Logger, StreamHandler
from . import easytrader
from .clock_engine import *
from .quotation_engine import *
from .event_engine import *
from .event_type import EventType
import time
from threading import Thread
import tushare as ts
import datetime

log = Logger(os.path.basename(__file__))
StreamHandler(sys.stdout).push_application()

PY_VERSION = sys.version_info[:2]
if PY_VERSION < (3, 5):
    raise Exception('Python 版本需要 3.5 或以上, 当前版本为 %s.%s 请升级 Python' % PY_VERSION)

ts.set_token('通联数据token')

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

        # 搞成线程
        self.is_active = True
        self.main_thread = Thread(target=self.main_manage)

        print('启动主引擎')

    def second_click(self, event):
        pass

    def start(self):
        """启动主引擎"""
        self.main_thread.start()

    def load_strategy(self):
        """动态加载策略，未完成，隔离策略之间的变量"""
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

    def main_manage(self):
        while self.is_active:
            today = datetime.date.today().strftime("%Y%m%d")
            mt = ts.Master()
            df = mt.TradeCal(exchangeCD='XSHG', beginDate=today, endDate=today, field='isOpen')
            is_open = df['isOpen'][0]
            if is_open:
                if int(time.localtime().tm_hour) > 8 and int(time.localtime().tm_hour) < 16:
                    if (not self.event_engine.is_alive()) or (not self.quotation_engine.is_alive()):
                        if self.event_engine.is_alive():
                            self.event_engine.stop()
                        if self.quotation_engine.is_alive():
                            self.quotation_engine.stop()
                        if self.clock_engine.is_alive():
                            self.clock_engine.stop()

                        time.sleep(1)
                        
                        self.event_engine.start()
                        self.quotation_engine.start()
                        self.clock_engine.start()
                    else:
                        testData = self.user.balance
                        if testData == None:
                            print("主引擎状态异常，重启中……")
                            if self.event_engine.is_alive():
                                self.event_engine.stop()
                            if self.quotation_engine.is_alive():
                                self.quotation_engine.stop()
                            if self.clock_engine.is_alive():
                                self.clock_engine.stop()
                        
                            time.sleep(1)
                        
                            self.event_engine.start()
                            self.quotation_engine.start()
                            self.clock_engine.start()
                        else:
                            print("主引擎状态正常，在此处更新日志")
                else:
                    if int(time.localtime().tm_hour) == 16 and int(time.localtime().tm_min) == 00:
                        testData = self.user.balance
                        print("今日交易结束，提交今日日志")

                    if self.event_engine.is_alive():
                        self.event_engine.stop()
                    if self.quotation_engine.is_alive():
                        self.quotation_engine.stop()
                    if self.clock_engine.is_alive():
                        self.clock_engine.stop()

                        time.sleep(1)
            else:
                if self.event_engine.is_alive():
                    self.event_engine.stop()
                if self.quotation_engine.is_alive():
                    self.quotation_engine.stop()
                if self.clock_engine.is_alive():
                    self.clock_engine.stop()

                time.sleep(1)

            time.sleep(3)
