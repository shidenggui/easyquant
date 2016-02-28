import datetime
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
    print(now_day)
    params = {'d': now_day}
    rep = requests.get(api, params)
    res = rep.json()[now_day]
    return True if res == 1 else False


def is_holiday_today():
    today = datetime.date.today().strftime('%Y%m%d')
    return is_holiday(today)

def is_tradetime_now():
    now_hour = datetime.datetime.now().hour
    now_minute = datetime.datetime.now().minute
    now = (now_hour, now_minute)
    if (9, 29) <= now <= (11, 31) or (12, 59) <= now <= (15, 1):
        return True
    return False

