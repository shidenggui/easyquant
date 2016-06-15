from easyquant import StrategyTemplate


class Strategy(StrategyTemplate):
    name = 'xq'

    def strategy(self, event):
        self.log.info('\n\nxq strategy')
        #self.log.info('检查持仓')
        #self.log.info(self.user.balance)
        #self.log.info('\n')
        if self.clock_engine.trading_state:
            self.log.info('trading')
        else:
            self.log.info('not trading')

    def __tracing(self):
        xqzh = {"ZH010389": 0.2, "ZH572114": 0.4, "ZH062130": 0.4}
        stocks = {}
        for pos in self.user.get_position():
            stocks[pos['stock_code']] = pos['market_value']

        for zh in xqzh:
            for pos in self.user.get_position(zh):
                stocks[pos['stock_code']] = stocks.get(pos['stock_code'], 0) - xqzh[zh] * pos['market_value']
        for code in stocks:
            if stocks[code] > 10000:
                try:
                    self.user.sell(code, 0, 0, stocks[code])
                except:
                    self.log.info('sell error')
        for code in stocks:
            if stocks[code] < -10000:
                try:
                    self.user.buy(code, 0, 0, -stocks[code])
                except:
                    self.log.info('buy error')

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
            self.__tracing()
