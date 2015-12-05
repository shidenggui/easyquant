# easyquant

基于 [easytrader](https://github.com/shidenggui/easytrader) 和 [easyquotation](https://github.com/shidenggui/easyquotation) 的简单量化交易框架


事件引擎借鉴 `vnpy` 


有兴趣的可以加群 `429011814` 一起交流

使用 `easyquotation` 每秒推送一次所有股票的五档行情
并调用策略执行

### requirements

* python 3.5
* pip install -r requirements.txt

### 使用 

在 `me.json` 中填入你的华泰信息，然后运行以下命令即可看到效果

[如何填写](https://github.com/shidenggui/easytrader)

```
python test.py
```

### 策略

策略用 `Python` 编写后置于 `strategies` 文件夹下
格式参考其中的 `Demo`

### 效果

```
启动主引擎
[2015-12-28 14:05:36.649599] INFO: main_engine.py: 加载策略: 策略1_Demo
[2015-12-28 14:05:36.650250] INFO: main_engine.py: 加载策略: 策略2_Demo
[2015-12-28 14:05:36.650713] INFO: main_engine.py: 加载策略完毕
触发每秒定时计时器



策略1触发
行情数据: 万科价格:  {'ask4': 0.0, 'ask1': 0.0, 'bid2_volume': 0, 'bid3': 0.0, 'bid5_volume': 0, 'name': '万  科Ａ', 'ask4_volume': 0, 'close': 24.43, 'volume': 0.0, 'ask3_volume': 0, 'bid5': 0.0, 'bid1': 0.0, 'ask2': 0.0, 'bid4_volume': 0, 'high': 0.0, 'ask5': 0.0, 'bid4': 0.0, 'ask5_volume': 0, 'turnover': 0, 'ask2_volume': 0, 'sell': 0.0, 'open': 0.0, 'bid3_volume': 0, 'bid2': 0.0, 'bid1_volume': 0, 'buy': 0.0, 'ask3': 0.0, 'low': 0.0, 'now': 0.0, 'ask1_volume': 0}
检查持仓
[{'asset_balance': 2758.98, 'market_value': 2740.9, 'enable_balance': 18.08, 'current_balance': 18.08, 'money_name': '人民币', 'fetch_balance': 18.08, 'money_type': '0'}]




策略2触发
行情数据: 华宝油气 {'ask4': 0.5, 'ask1': 0.497, 'bid2_volume': 4594100, 'bid3': 0.494, 'bid5_volume': 851300, 'name': '华宝油气', 'ask4_volume': 15650706, 'close': 0.5, 'volume': 138149552.799, 'ask3_volume': 19611307, 'bid5': 0.492, 'bid1': 0.496, 'ask2': 0.498, 'bid4_volume': 313700, 'high': 0.501, 'ask5': 0.501, 'bid4': 0.493, 'ask5_volume': 10108300, 'turnover': 277462973, 'ask2_volume': 10747730, 'sell': 0.497, 'open': 0.5, 'bid3_volume': 997500, 'bid2': 0.495, 'bid1_volume': 5507952, 'buy': 0.496, 'ask3': 0.499, 'low': 0.495, 'now': 0.497, 'ask1_volume': 14948518}
检查持仓
[{'asset_balance': 2758.98, 'market_value': 2740.9, 'enable_balance': 18.08, 'current_balance': 18.08, 'money_name': '人民币', 'fetch_balance': 18.08, 'money_type': '0'}]

```
