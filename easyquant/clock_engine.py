# coding: utf-8
import datetime
import time
from threading import Thread

from .event_engine import Event, EventEngine
from .event_type import EventType


class Clock:
    bTradingTime = False
    ClockEvent = 0  # 0:收市，从交易时间到收市推送一次，1,5,15,30,60开市时间推送

    def __init__(self, bTradingTime, clockevent):
        self.bTradingTime = bTradingTime
        self.ClockEvent = clockevent


class ClockEngine:
    """行情推送引擎"""
    presec = 0
    premin1 = 0
    premin5 = 0
    premin15 = 0
    premin30 = 0
    prehour = 0

    preTradingState = False

    tradeclock = [[datetime.time(9, 15, 0), datetime.time(11, 30, 0)],
                  [datetime.time(13, 00, 0), datetime.time(15, 00, 0)]]

    def __init__(self, event_engine):
        self.event_engine = event_engine
        self.is_active = True
        self.clockengine_thread = Thread(target=self.clocktick)
        self.sleep_time = 0.45
        nowtime = time.localtime(time.time())
        self.presec = nowtime.tm_sec
        self.premin1 = nowtime.tm_min - 1
        self.premin5 = (nowtime.tm_min / 5) * 5
        self.premin15 = (nowtime.tm_min / 15) * 15
        self.premin30 = (nowtime.tm_min / 30) * 30
        self.premin60 = nowtime.tm_hour

        nowclock = datetime.time(nowtime.tm_hour, nowtime.tm_min, nowtime.tm_sec)
        self.preTradingState = self.isTradingTime(nowclock)

    def isTradingTime(self, nowclock):
        for tradetime in self.tradeclock:
            if tradetime[0] < nowclock < tradetime[1]:
                return True
        return False

    def start(self):
        self.is_active = True
        self.clockengine_thread.start()
    
    def is_alive(self):
        return self.clockengine_thread.is_alive()

    def clocktick(self):
        while self.is_active:
            # nowtime = time.gmtime(time.time()) gmtime时区是0，time.localtime本地时区
            nowtime = time.localtime(time.time())
            if nowtime.tm_sec == self.presec:
                pass
            else:
                if nowtime.tm_wday in [5, 6]:
                    pass  # 周末，放假了
                else:
                    # 工作日，干活了
                    self.presec = nowtime.tm_sec
                    # print( nowtime.tm_sec )

                    nowclock = datetime.time(nowtime.tm_hour, nowtime.tm_min, nowtime.tm_sec)
                    if self.isTradingTime(nowclock) is True:
                        if self.preTradingState is False:
                            self.preTradingState = True
                            # print("开始交易时间")

                        if nowtime.tm_min != self.premin1:
                            self.premin1 = nowtime.tm_min
                            event = Event(event_type=EventType.CLOCK, data=Clock(self.preTradingState, 1))
                            self.event_engine.put(event)
                            # print("MIN1:%d" % (self.premin1))

                        if (nowtime.tm_min % 5 == 0) and (nowtime.tm_min != self.premin5):
                            self.premin5 = nowtime.tm_min
                            event = Event(event_type=EventType.CLOCK, data=Clock(self.preTradingState, 5))
                            self.event_engine.put(event)
                            # print("MIN5:%d" % (self.premin5))

                        if (nowtime.tm_min % 15 == 0) and (nowtime.tm_min != self.premin15):
                            self.premin15 = nowtime.tm_min
                            event = Event(event_type=EventType.CLOCK, data=Clock(self.preTradingState, 15))
                            self.event_engine.put(event)
                            # print("MIN15:%d" % (self.premin15))

                        if (nowtime.tm_min % 30 == 0) and (nowtime.tm_min != self.premin30):
                            self.premin30 = nowtime.tm_min
                            event = Event(event_type=EventType.CLOCK, data=Clock(self.preTradingState, 30))
                            self.event_engine.put(event)
                            # print("MIN30:%d" % (self.premin30))

                        if (nowtime.tm_min % 60 == 0) and (nowtime.tm_hour != self.prehour):
                            self.prehour = nowtime.tm_hour
                            event = Event(event_type=EventType.CLOCK, data=Clock(self.preTradingState, 60))
                            self.event_engine.put(event)
                            # print("MIN60:%d" % (self.prehour))
                    else:
                        if self.preTradingState is True:
                            self.preTradingState = False
                            event = Event(event_type=EventType.CLOCK, data=Clock(self.preTradingState, 0))
                            self.event_engine.put(event)
                            # print("交易时间结束")

            time.sleep(self.sleep_time)

    def stop(self):
        self.is_active = False


if __name__ == '__main__':
    ee = EventEngine()
    clock = ClockEngine(ee)
    clock.start()
