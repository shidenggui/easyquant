import sys
from datetime import timedelta, timezone

import easyquotation
from easyquant.push_engine.clock_engine import ClockEngine

import easyquant
from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine


quotation_engine = DefaultQuotationEngine

quotation_engine.PushInterval = 30

m = easyquant.MainEngine(broker='xq', need_data=sys.argv[1], quotation_engines=[quotation_engine], tzinfo=timezone(timedelta(hours=8)))
m.load_strategy()
m.start()
