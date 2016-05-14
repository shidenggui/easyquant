# coding: utf-8
import datetime
from threading import Thread
import time
import arrow
from dateutil import tz

from ..easydealutils import time as etime
from ..event_engine import Event


class Clock:
    def __init__(self, trading_time, clock_event):
        self.trading_state = trading_time
        self.clock_event = clock_event


class ClockEngine:
    """
    时间推送引擎
    1. 提供统一的 now 时间戳.
    """
    EventType = 'clock_tick'

    def __init__(self, event_engine, now=None, tzinfo=None):
        """
        :param event_engine:
        :param start_time:  issubclass(datetime.datetime) or arrow.Arrow 指定开始时间, 测试时可用.
        :param event_engine: tzinfo
        :return:
        """
        # 默认使用当地时间的时区
        self.tzinfo = tzinfo or tz.tzlocal()
        # 引擎启动的时间,默认为当前.测试时可手动设置模拟各个时间段.
        self.time_delta = self._delta(now)
        self.start_time = self.now_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        self.event_engine = event_engine
        self.is_active = True
        self.clock_engine_thread = Thread(target=self.clocktick)
        self.sleep_time = 1
        self.trading_state = True if etime.is_tradetime(datetime.datetime.now()) else False

    def _delta(self, now):
        if now is None:
            return 0
        if now.tzinfo is None:
            now = arrow.get(datetime.datetime(
                now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond, self.tzinfo,
            ))

        return (arrow.now() - now).total_seconds()

    @property
    def now(self):
        """
        now 时间戳统一接口
        :return:
        """
        return time.time() - self.time_delta

    @property
    def now_dt(self):
        """
        :return: datetime 类型, 带时区的时间戳.建议使用 arrow 库
        """
        return arrow.get(self.now).to(self.tzinfo)

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

        if etime.is_holiday(now_time):
            pass  # 假日暂停时钟引擎
        else:
            # 工作日，干活了
            if etime.is_tradetime(now_time):
                # 交易时间段
                if self.trading_state is True:
                    if etime.is_closing(now_time):
                        self.push_event_type('closing')

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

            elif self.trading_state is True:
                self.trading_state = False
                self.push_event_type('close')

    def push_event_type(self, etype):
        event = Event(event_type=self.EventType, data=Clock(self.trading_state, etype))
        self.event_engine.put(event)

    def stop(self):
        self.is_active = False
