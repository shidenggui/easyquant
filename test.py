import easyquant

print('easyquant 测试 DEMO')
print('请输入你使用的券商:')
choose = input('1: 华泰 2: 佣金宝 \n:')
broker = 'ht' if choose == '1' else 'yjb'


def get_broker_need_data(choose_broker):
    need_data = input('请输入你的帐号配置文件路径(直接回车使用 %s.json):' % choose_broker)
    if need_data == '':
        return '%s.json' % choose_broker
    return need_data

m = easyquant.MainEngine(broker, get_broker_need_data(broker))
m.load_strategy()
m.start()
