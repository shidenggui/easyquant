# coding: utf-8
import dill
from threading import Thread

import aiohttp

import time
from easyquant.event_engine import Event

ACCOUNT_OBJECT_FILE = 'account.session'


class BaseEngine:
    """行情推送引擎基类"""
    EventType = 'base'
    PushInterval = 1

    def __init__(self, event_engine, clock_engine):
        with open(ACCOUNT_OBJECT_FILE, 'rb') as f:
            self.user = dill.load(f)
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
                time.sleep(self.PushInterval)
                continue
            event = Event(event_type=self.EventType, data=response_data)
            self.event_engine.put(event)
            time.sleep(self.PushInterval)

    def fetch_quotation(self):
        # return your quotation
        return None

    def init(self):
        # do something init
        pass
