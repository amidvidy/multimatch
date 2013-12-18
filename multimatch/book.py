from __future__ import print_function

from itertools import chain
from collections import deque
from rbtree import rbtree

from log import get_logger
from trade import Trade
from orders import LimitBuyOrder, LimitSellOrder

logger = get_logger(__name__)

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

    def quote(self):
        return "BID: {0}, ASK: {1}".format(self.max_bid(), self.min_ask())

    def _add_entry(self, book, key, value):
        logger.info("Adding to book - price:{0} order:{1}".format(key, value))
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
            # Don't let the books get crossed
            assert (not self.has_bids() or self.max_bid() < remaining_ask.price)
            self._add_entry(self.asks, remaining_ask.price, remaining_ask)

    def fill_bid(self, bid):
        logger.info("Filling bid: {0}".format(bid))
        for (price, asks) in (ask.item for ask in self.asks.iternodes() if bid.price_matches(ask.key)):
            # remove the current node from the tree
            # current list of asks is not deleted since it is in scope, yay garbage collection
            del self.asks[price]
            for ask in (asks.popleft() for _ in xrange(len(asks))):
                (ask, bid) = self.make_trade(ask, bid, ask.price)
                if ask.quantity:
                    assert bid.quantity == 0
                    logger.debug("Partial fill for ask: {0}".format(ask))
                    # if we only partially filled the ask, our bid has been filled
                    # add the partially filled ask to the front of the order list and return
                    self.asks[price] = deque(chain([ask], asks))
                    return None
                if not bid.quantity:
                    # We filled both orders exactly
                    return None

        assert bid.quantity > 0
        # We will only reach this point if we failed to fill our order
        return bid

    # Logic is very similar to fill_bid
    # TODO: consolidate fill_bid and fill_ask into a generalized match method
    def fill_ask(self, ask):
        logger.info("Filling ask: {0}".format(ask))
        for (price, bids) in (bid.item for bid in self.bids.iternodes() if ask.price_matches(bid.key)):
            # remove the current node from the tree
            del self.bids[price]
            for bid in (bids.popleft() for _ in xrange(len(bids))):
                (ask, bid) = self.make_trade(ask, bid, bid.price)
                if bid.quantity:
                    assert ask.quantity == 0
                    logger.debug("Partial fill for bid: {0}".format(bid))
                    self.bids[price] = deque(chain([bid], bids))
                    return None
                if not ask.quantity:
                    return None

        assert ask.quantity > 0
        return ask

    def make_trade(self, ask, bid, price):
        # Don't give someone a lower price than what they asked
        assert price >= ask.price
        # Don't give someone a higher price than what they bid
        assert price <= bid.price
        # Sanity test: make sure the asset is corret
        assert ask.symbol == bid.symbol

        quantity = min(ask.quantity, bid.quantity)

        trade = Trade(ask.symbol, quantity, price, bid.trader_id, ask.trader_id)
        logger.info("Making trade: {0}".format(trade))
        self.trade_callback(trade)

        # return partials
        return (LimitSellOrder(ask.price, ask.symbol, ask.quantity - quantity, ask.trader_id),
                LimitBuyOrder(bid.price, bid.symbol, bid.quantity - quantity, bid.trader_id))

    def execute(self, order):
        order.execute(self)
