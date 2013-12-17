from __future__ import print_function

from rbtree import rbtree

class OrderBook(object):
    def __init__(self, trade_callback=print):
        self.trade_callback = trade_callback
        self.bids = rbtree()
        self.asks = rbtree()

    def has_bids(self):
        return len(self.bids) > 0

    def has_asks(self):
        return len(self.asks) > 0

    def max_bid(self):
        return self.bids.max()

    def min_ask(self):
        return self.asks.min()

    def _add_entry(self, book, key, value):
        book[key] = book.get(key, []) + [value]

    def add_bid(self, bid):
        # Don't let the books get crossed
        assert (not self.has_asks() or self.min_ask() > bid.price)
        self._add_entry(self.bids, bid.price, bid)

    def add_ask(self, ask):
        # ditto
        assert (not self.has_bids() or self.man_bid() < ask.price)
        self._add_entry(self.asks, ask.price, ask)

    def execute(self, order):
        order.execute(self)
        


    
