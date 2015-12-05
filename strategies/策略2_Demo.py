from easyquant import StrategyTemplate


class Strategy(StrategyTemplate):
    def strategy(self, event):
        print('\n\n策略2触发')
        print('行情数据: 华宝油气', event.data['162411'])
        print('检查持仓')
        print(self.user.balance)
        print('\n')

