# coding: utf-8
"""
演示如何进行单元测试
"""
import time
import unittest
import datetime
from easyquant.main_engine import MainEngine
from easyquant.push_engine.clock_engine import ClockEngine

__author__ = 'Shawn'

main_engine = MainEngine('ht')


class BaseTest(unittest.TestCase):
    """
    基础的配置
    """

    @property
    def main_engine(self):
        return main_engine

    @property
    def clock_engine(self):
        """
        :return:
        """
        return self.main_engine.clock_engine


class TestClock(BaseTest):
    """
    时钟的单元测试
    """

    @property
    def main_engine(self):
        return self._main_engine

    def setUp(self):
        """
        执行每个单元测试 前 都要执行的逻辑
        :return:
        """
        # 此处重新定义 main_engine
        self._main_engine = MainEngine('ht')

        # 设置为不在交易中
        self.clock_engine.trading_state = False

    def tearDown(self):
        """
        执行每个单元测试 后 都要执行的逻辑
        :return:
        """

    def test_tick(self):
        """
        测试时钟接口
        从开始前1分钟一直到收市后1分钟, 触发所有的已定义时钟事件
        :return:
        """
        # 各个时间间隔的触发次数计数
        counts = {
            0.5: 0,
            1: 0,
            5: 0,
            15: 0,
            30: 0,
            60: 0,
            "open": 0,
            "pause": 0,
            "continue": 0,
            "closing": 0,
            "close": 0,
        }

        def count(event):
            # 时钟引擎必定在上述的类型中
            self.assertIn(event.data.clock_event, counts)
            # 计数
            counts[event.data.clock_event] += 1

        # 注册一个响应时钟事件的函数
        self.main_engine.event_engine.register(ClockEngine.EventType, count)

        # 开启事件引擎
        self.main_engine.event_engine.start()

        # 模拟从开市前1分钟, 即8:59分, 到休市后1分钟的每秒传入时钟接口
        begin = datetime.datetime(2016, 5, 5, 8, 59)
        hours = 15 - 9
        mins = hours * 60 + 2
        seconds = 60 * mins
        for secs in range(seconds):
            now_time = begin + datetime.timedelta(seconds=secs)
            self.clock_engine.tock(now_time)

        # 等待事件引擎处理
        while self.main_engine.event_engine.queue_size > 1:
            pass
        time.sleep(.1)
        self.main_engine.event_engine.stop()

        # 核对次数, 休市的时候不会统计
        self.assertEqual(counts[60], 15 - 9 + 1 - len(["9:00", "12:00", "15:00"]))
        self.assertEqual(counts[30], (15 - 9) * 2 + 1 - len(["9:00", "11:30", "12:00", "12:30", "15:00"]))
        self.assertEqual(counts[15],
                         (15 - 9) * 4 + 1 - len(["9:00", "9:15", "11:30", "11:45", "12:00", "12:15", "12:30",
                                                 "12:45", "13:00", "15:00"]))

        # 开盘收盘, 中午开盘休盘, 必定会触发2次, 如果报错,说明是因为当前时间处于非交易日
        self.assertEqual(counts['open'], 2)
        self.assertEqual(counts['pause'], 1)
        self.assertEqual(counts['continue'], 1)
        self.assertEqual(counts['closing'], 1)
        self.assertEqual(counts['close'], 1)
