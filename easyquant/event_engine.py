from queue import Queue, Empty
from threading import Thread, Timer
from collections import defaultdict
from .event_type import EventType
import time


class Event:
    """事件对象"""

    def __init__(self, event_type, data=None):
        self.event_type = event_type
        self.data = data


class EventTimer:
    """计时器"""
    def __init__(self, interval_seconds, function):
        """计时器
        :param interval_seconds:计时间隔
        :param function:调用函数
        """
        self.__interval = interval_seconds
        self.__function = function
        self.is_active = True

    def start(self):
        self.is_active = True
        Timer(self.__interval, self.__loop).start()

    def __loop(self):
        if self.is_active:
            self.__function()
            Timer(self.__interval, self.__loop).start()

    def stop(self):
        self.is_active = False

    def whileloop(self):
        """取代 Timer 的一种实现"""
        while self.is_active:
            self.__function()
            time.sleep(self.__interval)


class EventEngine:
    """事件驱动引擎"""
    def __init__(self):
        """初始化事件引擎"""
        # 事件队列
        self.__queue = Queue()

        # 事件引擎开关
        self.__active = False

        # 计时器，用于触发计时事件
        self.__timer = EventTimer(interval_seconds=1, function=self.__on_timer)

        # 事件引擎处理线程
        self.__thread = Thread(target=self.__run)

        # 事件字典，key 为时间， value 为对应监听事件函数的列表
        self.__handlers = defaultdict(list)

    def __run(self):
        """启动引擎"""
        while self.__active:
            try:
                event = self.__queue.get(block=True, timeout=1)
                self.__process(event)
            except Empty:
                pass

    def __process(self, event):
        """事件处理"""
        # 检查该事件是否有对应的处理函数
        if event.event_type in self.__handlers:
            # 若存在,则按顺序将时间传递给处理函数执行
            for handler in self.__handlers[event.event_type]:
                handler(event)

    def __on_timer(self):
        """向事件队列中存入计时器事件"""
        event = Event(event_type=EventType.TIMER)
        self.put(event)

    def start(self):
        """引擎启动"""
        self.__active = True
        self.__thread.start()
        self.__timer.start()

    def stop(self):
        """停止引擎"""
        self.__active = False
        self.__timer.stop()
        self.__thread.join()
    
    def is_alive(self):
        """检查事件引擎处理线程状态"""
        return self.__thread.is_alive()

    def register(self, event_type, handler):
        """注册事件处理函数监听"""
        self.__handlers[event_type].append(handler)

    def unregister(self, event_type, handler):
        """注销事件处理函数"""
        handler_list = self.__handlers.get(event_type)
        if handler_list is None:
            return
        if handler in handler_list:
            handler_list.remove(event_type)
        if len(handler_list) == 0:
            self.__handlers.pop(event_type)

    def put(self, event):
        self.__queue.put(event)

    @property
    def queue_size(self):
        return self.__queue.qsize()
