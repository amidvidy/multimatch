from __future__ import print_function

import logging

from collections import deque
from rbtree import rbtree

from trade import Trade
from orders import LimitBuyOrder, LimitSellOrder

# TODO: logging

class OrderBook(object):
    def __init__(self, trade_callback=print):
        
        self.trade_callback = trade_callback
        self.asks = rbtree()
        # reverse comparator
        self.bids = rbtree(cmp=lambda x,y: y-x)

    def has_bids(self):
        return len(self.bids) > 0

    def has_asks(self):
        return len(self.asks) > 0

    def max_bid(self):
        # reverse comparator
        return self.bids.min()

    def min_ask(self):
        return self.asks.min()

    def _add_entry(self, book, key, value):
        entries = book.get(key, deque())
        entries.append(value)
        book[key] = entries

    def add_bid(self, bid):
        remaining_bid = self.fill_bid(bid)
        
        if remaining_bid:
            # Don't let the books get crossed
            assert (not self.has_asks() or self.min_ask() > remaining_bid.price)
            self._add_entry(self.bids, remaining_bid.price, remaining_bid)

    def add_ask(self, ask):
        remaining_ask = self.fill_ask(ask)
        
        if remaining_ask:
            assert (not self.has_bids() or self.max_bid() < remaining_ask.price)
            self._add_entry(self.asks, remaining_ask.price, remaining_ask)

    def fill_bid(self, bid):
        # get any asks that match our bid
        askgen = (ask.item for ask in self.asks.iternodes() if ask.key <= bid.price)
        while bid.quantity:
            try:
                (price, asks) = next(askgen)
                while asks:
                    # fill asks in the order they were submitted
                    ask = asks.popleft()
                    (ask, bid) = self.make_trade(ask, bid)
                    if ask.quantity:
                        # we filled our order
                        # put the partially filled ask back on the list
                        asks.appendleft(ask)
                        break
                # remove empty nodes from the tree
                if not asks:
                    del self.asks[price]

            except StopIteration:
                # order is partially filled, return whatever is unfilled to add to the book
                return bid
        
    def fill_ask(self, ask):
        bidgen = (bid.item for bid in self.bids.iternodes() if bid.key >= ask.price)
        while ask.quantity:
            try:
                (price, bids) = next(bidgen)
                while bids:
                    bid = bids.popleft()
                    (ask, bid) = self.make_trade(ask, bid)
                    if bid.quantity:
                        # if we only partially filled their order, ours is filled
                        # put the partially filled bid back on the list
                        bids.appendleft(bid)
                        break
                # remove empty nodes from the tree
                if not bids:
                    del self.bids[price]

            except StopIteration:
                # order is partiailly filled, return whatever is unfilled to add to the bock
                return ask

    def make_trade(self, ask, bid):
        assert ask.price <= bid.price
        assert ask.symbol == bid.symbol
        
        quantity = min(ask.quantity, bid.quantity)
        
        self.trade_callback(Trade(ask.symbol, quantity, ask.price, bid.trader_id, ask.trader_id))

        # return partials
        return (LimitSellOrder(ask.price, ask.symbol, ask.quantity - quantity, ask.trader_id), 
                LimitBuyOrder(bid.price, bid.symbol, bid.quantity - quantity, bid.trader_id))

    def execute(self, order):
        order.execute(self)
