from __future__ import print_function

from collections import deque
from rbtree import rbtree

from trade import Trade
from orders import LimitBuyOrder, LimitSellOrder

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
        bids = (ask.item for ask in self.asks.iternodes() if ask.key <= bid.price)
        while bid.quantity:
            try:
                (price, asks) = next(bids)
                while asks:
                    # fill asks in the order they were submitted
                    ask = asks.popleft()
                    (ask, bid) = self.make_trade(ask, bid)
                    if bid is None:
                        # put the partially filled ask back on the list
                        asks.appendleft(ask)
                        # done
                        break
                # remove empty nodes from the tree
                del self.asks[price]

            except StopIteration:
                return bid
        
    def fill_ask(self, ask):
        return ask

    def make_trade(self, ask, bid):
        assert ask.price <= bid.price
        assert ask.symbol == bid.symbol
        
        quantity = min(ask.quantity, bid.quantity)
        
        self.trade_callback(Trade(ask.symbol, quantity, ask.price, bid.trader_id, ask.trader_id))

        if quantity == ask.quantity:
            # Filled the ask
            return (None, LimitBuyOrder(bid.price, bid.symbol, bid.quantity - quantity, bid.trader_id))
        else:
            # Filled the bid
            return (LimitSellOrder(ask.price, ask.symbol, ask.quantity - quantity, ask.trader_id, None))

    def execute(self, order):
        order.execute(self)
        print(self.asks)
