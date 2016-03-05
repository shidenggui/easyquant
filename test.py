import easyquant
from easyquant import DefaultQuotationEngine, DefaultLogHandler

print('easyquant 测试 DEMO')
print('请输入你使用的券商:')
choose = input('1: 华泰 2: 佣金宝 3: 银河 4: 雪球模拟组合\n:')

broker = 'ht'
if choose == '2':
    broker = 'yjb'
elif choose == '3':
    broker = 'yh'
elif choose == '4':
    broker = 'xq'


def get_broker_need_data(choose_broker):
    need_data = input('请输入你的帐号配置文件路径(直接回车使用 %s.json):' % choose_broker)
    if need_data == '':
        return '%s.json' % choose_broker
    return need_data


need_data = get_broker_need_data(broker)

push_interval = int(input('请输入行情推送间隔(s):'))
DefaultQuotationEngine.PushInterval = push_interval

log_type_choose = input('请输入 log 记录方式: 1: 显示在屏幕 2: 记录在指定文件')
log_type = 'stdout' if log_type_choose == '1' else 'file'

if log_type == 'file':
    log_filepath = input('请输入 log 文件记录路径')

log_handler = DefaultLogHandler(name='测试1', log_type=log_type, filepath=log_filepath)

m = easyquant.MainEngine(broker, need_data, quotation_engines=[DefaultQuotationEngine], log_handler=log_handler)
m.load_strategy()
m.start()
