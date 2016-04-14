# coding: utf-8

import easyquotation

from .base_engine import BaseEngine


class DefaultQuotationEngine(BaseEngine):
    """新浪行情推送引擎"""
    EventType = 'quotation'

    def init(self):
        self.source = easyquotation.use('sina')

    def fetch_quotation(self):
        return self.source.all
