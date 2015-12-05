import easyquant

m = easyquant.MainEngine('ht', 'me.json')
m.load_strategy()
m.start()
