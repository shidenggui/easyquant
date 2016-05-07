
from custom import fixedmainengine

m = fixedmainengine.FixedMainEngine("ht", ext_stocks=['159915'])
m.load_strategy()
m.start()
