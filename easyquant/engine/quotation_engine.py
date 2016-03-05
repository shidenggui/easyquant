# coding: utf-8
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
from event import EventType
from threading import Thread
import easyquotation
from .event_engine import Event
from .engine import Engine

class Quotation(Engine):
    """行情推送引擎"""

    def __init__(self, event_engine):
        self.event_engine = event_engine
        self.is_active = True
        self.source = easyquotation.use('sina')
        self.quotation_thread = Thread(target=self.get_quotation)
        self.sleep_time = 1

    def start(self):
        self.quotation_thread.start()

    def get_quotation(self):
        while self.is_active:
            response_data = self.source.all
            event = Event(event_type=EventType.QUOTATION, data=response_data)
            self.event_engine.put(event)
            time.sleep(self.sleep_time)

    def stop(self):
        self.is_active = False


if __name__ == '__main__':
    pass
