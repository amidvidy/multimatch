from __future__ import print_function

from collections import defaultdict

from book import OrderBook

class MultiBook(object):

    def __init__(self, trade_callback=print):
        self.trade_callback = trade_callback
        self.books = defaultdict(lambda: OrderBook(self.trade_callback))
    
    def get_book(self, symbol):
        return self.books[symbol]

    def execute(self, order):
        self.books[order.symbol].execute(order)
        
    
