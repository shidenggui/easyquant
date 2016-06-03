import easyquotation
from easyquant.push_engine.clock_engine import ClockEngine

import easyquant
from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine

print('easyquant 测试 DEMO')
print('请输入你使用的券商:')
choose = input('1: 华泰 2: 佣金宝 3: 银河 4: 雪球模拟组合 5: 广发\n:')

broker = 'ht'
if choose == '2':
    broker = 'yjb'
elif choose == '3':
    broker = 'yh'
elif choose == '4':
    broker = 'xq'
elif choose == '5':
    broker = 'gf'


def get_broker_need_data(choose_broker):
    need_data = input('请输入你的帐号配置文件路径(直接回车使用 %s.json)\n:' % choose_broker)
    if need_data == '':
        return '%s.json' % choose_broker
    return need_data


need_data = get_broker_need_data(broker)


class LFEngine(PushBaseEngine):
    EventType = 'lf'

    def init(self):
        self.source = easyquotation.use('lf')

    def fetch_quotation(self):
        return self.source.stocks(['162411', '000002'])

quotation_choose = input('请输入使用行情引擎 1: sina 2: leverfun 十档 行情(目前只选择了 162411, 000002)\n:')

quotation_engine = DefaultQuotationEngine if quotation_choose == '1' else LFEngine

push_interval = int(input('请输入行情推送间隔(s)\n:'))
quotation_engine.PushInterval = push_interval

log_type_choose = input('请输入 log 记录方式: 1: 显示在屏幕 2: 记录到指定文件\n: ')
log_type = 'stdout' if log_type_choose == '1' else 'file'

log_filepath = input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''

log_handler = DefaultLogHandler(name='测试', log_type=log_type, filepath=log_filepath)


m = easyquant.MainEngine(broker, need_data, quotation_engines=[quotation_engine], log_handler=log_handler)
m.load_strategy()
m.start()
