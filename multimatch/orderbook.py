from rbtree import rbtree

class OrderBook(object):
    def __init__(self):
        self.bids = rbtree()
        self.asks = rbtree()

    def add_bid(self, order):
        self.bids[order.price] = order
