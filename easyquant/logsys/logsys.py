import os
import sys
from logbook import Logger, StreamHandler, FileHandler
import logbook
logbook.set_datetime_format('local')

class LogSys(object):
    """Log系统类"""
    def __init__(self, logtype, filename, loglevel = 'DEBUG'):
        """Log对象
        :logtype: stream 类型, file 类型
        :filename: 关联文件名
        :loglevel: 设定log等级
        """
        self.log = Logger(filename)
        if logtype == 'stream':
            StreamHandler(sys.stdout, level=loglevel).push_application()
        if logtype == 'file':
            bool(os.path.exists('./log')) or os.makedirs('./log')
            FileHandler('./log/' + filename + '.log', level=loglevel).push_application() 
    """
    封装LogLevel
    """
    def warn(self, content):
        self.log.warn(content)

    def info(self, content):
        self.log.info(content)

    def debug(self, content):
        self.log.info(content)

    def critical(self, content):
        self.log.critical(content)

    def error(self, content):
        self.log.error(content)

    def notice(self, content):
        self.log.notice(content)
"""
def main():
    log = LogSys('stream', 'euxyacg', loglevel='DEBUG')
    log.warn('warning, euxyacg')
    log.info('info, euxyacg')
    log.debug('debug, euxyacg')
    log.critical('critical, euxyacg')
    log.error('error, euxyacg')
    log.notice('notice, euxyacg')

if __name__ == '__main__':
    main()
"""
            
