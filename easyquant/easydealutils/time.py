import datetime
import time
from functools import wraps

import requests


def memcache(func):
    cache = {}

    @wraps(func)
    def wrap(*args):
        if args not in cache:
            cache[args] = func(args)
        return cache[args]

    return wrap


@memcache
def is_holiday(day):
    api = 'http://www.easybots.cn/api/holiday.php'
    now_day = datetime.date.today().strftime('%Y%m%d')
    params = {'d': now_day}
    rep = requests.get(api, params)
    res = rep.json()[now_day]
    return True if res == 1 else False


def is_holiday_today():
    today = datetime.date.today().strftime('%Y%m%d')
    return is_holiday(today)


def is_tradetime_now():
    now_time = time.localtime()
    now = (now_time.tm_hour, now_time.tm_min, now_time.tm_sec)
    if (9, 15, 0) <= now <= (11, 30, 0) or (13, 0, 0) <= now <= (25, 0, 0):
        return True
    return False


def calc_next_trade_time_delta_seconds():
    now_time = datetime.datetime.now()
    now = (now_time.hour, now_time.minute, now_time.second)
    if now < (9, 15, 0):
        next_trade_start = now_time.replace(hour=9, minute=15, second=0)
    elif (12, 0, 0) < now < (13, 0, 0):
        next_trade_start = now_time.replace(hour=13, minute=0, second=0)
    elif now > (15, 0, 0):
        next_trade_start = now_time.replace(day=now_time.day + 1, hour=9, minute=15, second=0)
    else:
        return 0
    time_delta = next_trade_start - now_time
    return time_delta.total_seconds()
