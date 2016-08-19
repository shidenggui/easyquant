import time
import datetime as dt
from dateutil import tz
from easyquant import DefaultLogHandler
from easyquant import StrategyTemplate


class Strategy(StrategyTemplate):
    name = '测试策略1'

    def init(self):
        # 通过下面的方式来获取时间戳
        now_dt = self.clock_engine.now_dt
        now = self.clock_engine.now
        now = time.time()

        # 注册时钟事件
        clock_type = "盘尾"
        moment = dt.time(14, 56, 30, tzinfo=tz.tzlocal())
        self.clock_engine.register_moment(clock_type, moment)

        # 注册时钟间隔事件, 不在交易阶段也会触发, clock_type == minute_interval
        minute_interval = 1.5
        self.clock_engine.register_interval(minute_interval, trading=False)

    def strategy(self, event):
        """:param event event.data 为所有股票的信息，结构如下
        {'162411':
        {'ask1': '0.493',
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
         'volume': '206390073.351'}}
        """
        # 使用 self.user 来操作账户，用法同 easytrader 用法
        # 使用 self.log.info('message') 来打印你所需要的 log
        print('demo1 的 log 使用自定义 log 的方式记录在 demo1.log')
        self.log.info('\n\n策略1触发')
        self.log.info('行情数据: 万科价格: %s' % event.data['000002'])
        self.log.info('检查持仓')
        self.log.info(self.user.balance)
        self.log.info('\n')

    def clock(self, event):
        """在交易时间会定时推送 clock 事件
        :param event: event.data.clock_event 为 [0.5, 1, 3, 5, 15, 30, 60] 单位为分钟,  ['open', 'close'] 为开市、收市
            event.data.trading_state  bool 是否处于交易时间
        """
        if event.data.clock_event == 'open':
            # 开市了
            self.log.info('open')
        elif event.data.clock_event == 'close':
            # 收市了
            self.log.info('close')
        elif event.data.clock_event == 5:
            # 5 分钟的 clock
            self.log.info("5分钟")

    def log_handler(self):
        """自定义 log 记录方式"""
        return DefaultLogHandler(self.name, log_type='stdout', filepath='demo1.log')

    def shutdown(self):
        """
        关闭进程前的调用
        :return:
        """
        self.log.info("假装在关闭前保存了策略数据")
