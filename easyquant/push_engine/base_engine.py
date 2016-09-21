# coding: utf-8
import time
from threading import Thread

import aiohttp

from easyquant.event_engine import Event

ACCOUNT_OBJECT_FILE = 'account.session'


class BaseEngine:
    """行情推送引擎基类"""
    EventType = 'base'
    PushInterval = 1

    def __init__(self, event_engine, clock_engine):
        self.event_engine = event_engine
        self.clock_engine = clock_engine
        self.is_active = True
        self.quotation_thread = Thread(target=self.push_quotation, name="QuotationEngine.%s" % self.EventType)
        self.quotation_thread.setDaemon(False)
        self.init()

    def start(self):
        self.quotation_thread.start()

    def stop(self):
        self.is_active = False

    def push_quotation(self):
        while self.is_active:
            try:
                response_data = self.fetch_quotation()
            except aiohttp.errors.ServerDisconnectedError:
                self.wait()
                continue
            event = Event(event_type=self.EventType, data=response_data)
            self.event_engine.put(event)
            self.wait()

    def fetch_quotation(self):
        # return your quotation
        return None

    def init(self):
        # do something init
        pass

    def wait(self):
        interval = self.PushInterval
        if interval < 1:
            time.sleep(interval)
            return
        else:
            time.sleep(self.PushInterval - int(interval))
            interval = int(interval)
            while interval > 0 and self.is_active:
                time.sleep(1)
                interval -= 1
