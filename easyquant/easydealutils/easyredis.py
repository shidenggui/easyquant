# coding: utf-8
import os
import sys
import redis
import json

from ..log_handler import DefaultLogHandler

class RedisIo(object):
    """Redis操作类"""
    
    def __init__(self, conf):
        self.config = self.file2dict(conf)
        if self.config['passwd'] is None:
            self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'])
        else:
            self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'], password = self.config['passwd'])
        self.log = self.log_handler()
    
    def file2dict(self, path):
        with open(path) as f:
            return json.load(f)
        
    def cleanup(self):
        self.r.flushdb()

    def lookup_redist_info(self):
        info = self.r.info()
        for key in info:
            self.log.info('%s:%s' % (key, info[key]))

    def set_key_value(self, key, value):
        self.r.set(key, value)

    def get_key_value(self, key):
        return self.r.get(key)

    def save(self):
        return self.r.save()

    def get_keys(self):
        return self.r.keys()

    def delete_key(self, key):
        return self.r.delete(key)

    def push_list_value(self, listname, value):
        return self.r.lpush(listname, value)

    def pull_list_range(self, listname, starpos, endpos):
        return self.r.lrange(listname, starpos, endpos)

    def get_list_len(self, listname):
        return self.r.llen(listname)
   
    def log_handler(self):
        """重定向日志"""
        return DefaultLogHandler()

def main():
    ri = RedisIo('redis.conf')
    ri.lookup_redist_info()

if __name__ == '__main__':
    main()
