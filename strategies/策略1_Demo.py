import time
import os
import sys

from easyquant import StrategyTemplate

class Strategy(StrategyTemplate):
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
        self.log = self.log_instance('stream', os.path.basename(__file__))
        self.log.info('\n\n策略1触发')
        self.log.info('行情数据: 万科价格: ', event.data['000002'])
        self.log.info('检查持仓')
        self.log.info(self.user.balance)
        self.log.info('\n')

    def clock(self, event):
        if event.data.ClockEvent == 0:
            print(time.strftime("\n%m-%d %H:%M:%S", time.localtime()))
        elif event.data.ClockEvent == 5:
            print("5分钟")
        elif event.data.ClockEvent == 30:
            print("30分钟")
