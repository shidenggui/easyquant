from easyquant import StrategyTemplate


class Strategy(StrategyTemplate):
    name = '测试策略2'

    def strategy(self, event):
        self.log.info('\n\n策略2触发')
        self.log.info('行情数据: 华宝油气 %s' % event.data['162411'])
        self.log.info('检查持仓')
        self.log.info(self.user.balance)
        self.log.info('\n')

