import time

from easyquant import StrategyTemplate


class Strategy(StrategyTemplate):
    def strategy(self, event):
        print('\n\n策略2触发')
        print('行情数据: 华宝油气', event.data['162411'])
        print('检查持仓')
        print(self.user.balance)
        print('\n')
        pass

    def clock(self, event):
        if event.data.ClockEvent == 0:
            print(time.strftime("\n%m-%d %H:%M:%S", time.localtime()))
        elif event.data.ClockEvent == 5:
            print("5分钟")
        elif event.data.ClockEvent == 30:
            print("30分钟")
