import os
import sys
import importlib
from collections import OrderedDict
from logbook import Logger, StreamHandler
from . import easytrader
from .quotation_engine import *
from .event_engine import *
from .event_type import EventType

log = Logger(os.path.basename(__file__))
StreamHandler(sys.stdout).push_application()


class MainEngine:
    """主引擎，负责行情 / 事件驱动引擎 / 交易"""

    def __init__(self, broker, need_data='me.json'):
        """初始化事件 / 行情 引擎并启动事件引擎
        """
        self.user = easytrader.use(broker)
        self.user.prepare(need_data)

        self.event_engine = EventEngine()
        self.quotation_engine = Quotation(self.event_engine)

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
        log.info('加载策略完毕')

    def quotation_test(self, event):
        """:param event event.data 为所有股票的信息，结构如下
        [{'ask1': '0.493',
         'ask1_volume': '75500',
         'ask2': '0.494',
         'ask2_volume': '7699281',
         'ask3': '0.495',
         'ask3_volume': '2262666',
         'ask4': '0.496',
         'ask4_volume': '1579300',
         'ask5': '0.497',
         'ask5_volume': '901600',
         'bid1': '0.492',
         'bid1_volume': '10765200',
         'bid2': '0.491',
         'bid2_volume': '9031600',
         'bid3': '0.490',
         'bid3_volume': '16784100',
         'bid4': '0.489',
         'bid4_volume': '10049000',
         'bid5': '0.488',
         'bid5_volume': '3572800',
         'buy': '0.492',
         'close': '0.499',
         'high': '0.494',
         'low': '0.489',
         'name': '华宝油气',
         'now': '0.493',
         'open': '0.490',
         'sell': '0.493',
         'turnover': '420004912',
         'volume': '206390073.351'}]
        """
        print('触发行情')
        print('检查持仓')
        print(self.user.position)
        print('触发策略')
        print('检查 %s 价格 %s' % ('162411', event.data['162411']['now']))
        print(event.data['162411'])
