import easyquant

print('easyquant 测试 DEMO')
print('请输入你使用的券商:')
choose = input('1: 华泰 2: 佣金宝 \n:')
broker = 'ht' if choose == '1' else 'yjb'

if broker == 'ht':
    need_data = input('请输入你的华泰帐号配置文件路径(直接回车使用 me.json):')
    if need_data == '':
        need_data = 'me.json'
elif broker == 'yjb':
    need_data = input('请输入你的佣金宝 token:')

m = easyquant.MainEngine(broker, need_data)
m.load_strategy()
m.start()
