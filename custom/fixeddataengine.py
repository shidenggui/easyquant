# !/usr/bin/python
# vim: set fileencoding=utf8 :
#
__author__ = 'keping.chu'

import easyquotation
from easyquant import PushBaseEngine # 引入行情引擎的基类


class FixedDataEngine(PushBaseEngine):
    EventType = 'custom'
    PushInterval = 15

    def __init__(self, event_engine, watch_stocks=None, s='sina'):

        self.watch_stocks = watch_stocks
        self.s = s
        self.source = None
        super(FixedDataEngine, self).__init__(event_engine)

    def init(self):
        # 进行相关的初始化操作
        self.source = easyquotation.use(self.s)

    def fetch_quotation(self):
        # 返回行情
        return self.source.stocks(self.watch_stocks)