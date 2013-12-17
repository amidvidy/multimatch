from __future__ import print_function
class Order(object):
    def __init__(self, symbol, quantity, trader_id, *args, **kwargs):
        self.symbol = symbol
        self.quantity = quantity
        self.trader_id = trader_id
        
    def __repr__(self):
        return "{0}(symbol={1}, quantity={2}, trader_id={3})".format(self.__class__.__name__,
                                                                     self.symbol,
                                                                     self.quantity,
                                                                     self.trader_id)

    def execute(self, book):
        raise NotImplementedError("Order is abstract!")

class MarketBuyOrder(Order):
    def __init__(self, *args, **kwargs):
        super(MarketBuyOrder, self).__init__(*args, **kwargs)
        self.price = float("inf")

    def execute(self, book):
        book.fill_bid(self)

class MarketSellOrder(Order):
    def __init__(self, *args, **kwargs):
        super(MarketSellOrder, self).__init__(*args, **kwargs)
        self.price = float("-inf")

    def execute(self, book):
        book.fill_ask(self)

class LimitBuyOrder(Order):
    def __init__(self, price, *args, **kwargs):
        super(LimitBuyOrder, self).__init__(*args, **kwargs)
        self.price = price
        
    def execute(self, book):
        book.add_bid(self)

class LimitSellOrder(Order):
    def __init__(self, price, *args, **kwargs):
        super(LimitSellOrder, self).__init__(*args, **kwargs)
        self.price = price

    def execute(self, book):
        book.add_ask(self)

