# coding: utf-8
import datetime
from threading import Thread

import time
from ..easydealutils import time as etime
from ..event_engine import Event


class Clock:
    def __init__(self, trading_time, clock_event):
        self.trading_state = trading_time
        self.clock_event = clock_event


class ClockEngine:
    """时间推送引擎"""
    EventType = 'clock_tick'

    def __init__(self, event_engine):
        self.start_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.event_engine = event_engine
        self.is_active = True
        self.clock_engine_thread = Thread(target=self.clocktick)
        self.sleep_time = 1
        self.trading_state = True if etime.is_tradetime(datetime.datetime.now()) else False

    def start(self):
        self.clock_engine_thread.start()

    def clocktick(self):
        while self.is_active:
            now_time = datetime.datetime.now()
            self.tock(now_time)
            time.sleep(self.sleep_time)

    def tock(self, now_time):
        """
        :param now_time: datetime.datetime()
        :return:
        """
        min_seconds = 60
        time_delta = now_time - self.start_time
        seconds_delta = int(time_delta.total_seconds())

        if etime.is_holiday_today():
            pass
        elif etime.is_tradetime(now_time):  # 工作日，干活了
            if self.trading_state is True:
                for delta in [0.5, 1, 5, 15, 30, 60]:

                    if seconds_delta % (min_seconds * delta) == 0:
                        self.push_event_type(delta)
            else:
                self.trading_state = True
                self.push_event_type('open')

        elif etime.is_pause(now_time):
            self.push_event_type('pause')

        elif etime.is_continue(now_time):
            self.push_event_type('continue')

        elif etime.is_closing(now_time):
            self.push_event_type('closing')

        elif self.trading_state is True:
            self.trading_state = False
            self.push_event_type('close')

    def push_event_type(self, etype):
        event = Event(event_type=self.EventType, data=Clock(self.trading_state, etype))
        self.event_engine.put(event)

    def stop(self):
        self.is_active = False
