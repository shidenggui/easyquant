import datetime
import doctest
from functools import lru_cache

import requests


@lru_cache()
def _is_holiday(day):
    # 该接口可能将于 2016.7.1 过期, 请关注该主页
    api = 'http://www.easybots.cn/api/holiday.php'
    params = {'d': day}
    rep = requests.get(api, params)
    res = rep.json()[day if isinstance(day, str) else day[0]]
    return True if res == "1" else False


def is_holiday(now_time):
    today = now_time.strftime('%Y%m%d')
    return _is_holiday(today)


def is_trade_date(now_time):
    return not is_holiday(now_time)


def get_next_trade_date(now_time):
    """
    :param now_time: datetime.datetime
    :return:
    >>> import datetime
    >>> get_next_trade_date(datetime.date(2016, 5, 5))
    datetime.date(2016, 5, 6)
    """
    now = now_time
    max_days = 365
    days = 0
    while 1:
        days += 1
        now += datetime.timedelta(days=1)
        if is_trade_date(now):
            if isinstance(now, datetime.date):
                return now
            else:
                return now.date()
        if days > max_days:
            raise ValueError('无法确定 %s 下一个交易日' % now_time)


OPEN_TIME = (
    (datetime.time(9, 15, 0), datetime.time(11, 30, 0)),
    (datetime.time(13, 0, 0), datetime.time(15, 0, 0)),
)


def is_tradetime(now_time):
    """
    :param now_time: datetime.time()
    :return:
    """
    now = now_time.time()
    for begin, end in OPEN_TIME:
        if begin <= now < end:
            return True
    else:
        return False


PAUSE_TIME = (
    (datetime.time(11, 30, 0), datetime.time(12, 59, 30)),
)


def is_pause(now_time):
    """
    :param now_time:
    :return:
    """
    now = now_time.time()
    for b, e in PAUSE_TIME:
        if b <= now < e:
            return True


CONTINUE_TIME = (
    (datetime.time(12, 59, 30), datetime.time(13, 0, 0)),
)


def is_continue(now_time):
    now = now_time.time()
    for b, e in CONTINUE_TIME:
        if b <= now < e:
            return True
    return False


CLOSE_TIME = (
    datetime.time(15, 0, 0),
)


def is_closing(now_time, start=datetime.time(14, 54, 30)):
    now = now_time.time()
    for close in CLOSE_TIME:
        if start <= now < close:
            return True
    return False

if __name__ == "__main__":
    doctest.testmod()