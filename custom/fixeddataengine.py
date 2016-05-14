# !/usr/bin/python
# vim: set fileencoding=utf8 :
#
__author__ = 'keping.chu'

import easyquotation
from easyquant import PushBaseEngine
import aiohttp
from easyquant.easydealutils import time as work_time
import time
from easyquant.event_engine import Event
import multiprocessing as mp
from threading import Thread


class FixedDataEngine(PushBaseEngine):
    EventType = 'custom'
    PushInterval = 15

    def __init__(self, event_engine, watch_stocks=None, s='sina'):

        self.watch_stocks = watch_stocks
        self.s = s
        self.source = None
        self.__queue = mp.Queue(1000)
        self.is_pause = False if work_time.is_tradetime_now() else True
        self._control_thread = Thread(target=self._process_control)
        self._control_thread.start()
        super(FixedDataEngine, self).__init__(event_engine)

    def _process_control(self):

        while True:
            try:
                msg = self.__queue.get(block=True)
                if msg == "pause":
                    self.is_pause = True
                else:
                    self.is_pause = False
            except:
                pass

    def pause(self):
        self.__queue.put("pause")

    def work(self):
        self.__queue.put("work")

    def init(self):
        # 进行相关的初始化操作
        self.source = easyquotation.use(self.s)

    def fetch_quotation(self):
        # 返回行情
        return self.source.stocks(self.watch_stocks)

    def push_quotation(self):
        while self.is_active:
            if self.is_pause:
                time.sleep(1)
                continue
            try:
                response_data = self.fetch_quotation()
            except aiohttp.errors.ServerDisconnectedError:
                time.sleep(self.PushInterval)
                continue
            event = Event(event_type=self.EventType, data=response_data)
            self.event_engine.put(event)
            time.sleep(self.PushInterval)
