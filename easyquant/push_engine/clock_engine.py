# coding: utf-8
import datetime
import time
from threading import Thread

from ..easydealutils import time as etime
from ..event_engine import Event


class Clock:
    bTradingTime = False
    ClockEvent = 0  # 0:收市，从交易时间到收市推送一次，0.5,1,5,15,30,60开市时间推送

    def __init__(self, bTradingTime, clockevent):
        self.bTradingTime = bTradingTime
        self.ClockEvent = clockevent


class ClockEngine:
    """时间推送引擎"""
    EventType = 'clock_tick'

    def __init__(self, event_engine):
        self.start_time = datetime.datetime.now()
        self.event_engine = event_engine
        self.is_active = True
        self.clockengine_thread = Thread(target=self.clocktick)
        self.sleep_time = 1
        self.preTradingState = True if etime.is_tradetime_now() else False

    def start(self):
        self.clockengine_thread.start()

    def clocktick(self):
        min_seconds = 60
        while self.is_active:
            now_time = datetime.datetime.now()
            time_delta = now_time - self.start_time
            seconds_delta = int(time_delta.total_seconds())
            # 防止 seconds_delta 为 0 时 % 都为 0
            if seconds_delta == 0:
                seconds_delta += 1
            if etime.is_holiday_today():
                pass
            elif not etime.is_tradetime_now():
                self.preTradingState = False
                event = Event(event_type=self.EventType, data=Clock(self.preTradingState, 0))
                self.event_engine.put(event)
                sleep_time = etime.calc_next_trade_time_delta_seconds() + 1
                time.sleep(sleep_time)
            elif etime.is_tradetime_now():  # 工作日，干活了
                self.preTradingState = True
                for delta in [0.5, 1, 5, 15, 30, 60]:
                    if seconds_delta % (min_seconds * delta) == 0:
                        event = Event(event_type=self.EventType, data=Clock(self.preTradingState, delta))
                        self.event_engine.put(event)

            time.sleep(self.sleep_time)

    def stop(self):
        self.is_active = False
