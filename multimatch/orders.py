from __future__ import print_function

class Order(object):
    def __init__(self, symbol, quantity, price, *args, **kwargs):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price

    def execute(self, book):
        raise NotImplementedError("Must instantiate a subtype")

class MarketBuyOrder(Order):
    def __init__(self, *args, **kwargs):
        super(MarketBuyOrder, self).__init__(*args, **kwargs)

    def execute(self, book):
        pass

class MarketSellOrder(Order):
    def __init__(self, *args, **kwargs):
        super(MarketSellOrder, self).__init__(*args, **kwargs)

    def execute(self, book):
        pass

class LimitBuyOrder(Order):
    def __init__(self, *args, **kwargs):
        super(LimitBuyOrder, self).__init__(*args, **kwargs)
        
    def execute(self, book):
        if book.has_asks() and book.min_ask() <= self.price:
            print("We can match this order")
        else:
            book.add_bid(self)

class LimitSellOrder(Order):
    def __init__(self, *args, **kwargs):
        super(LimitSellOrder, self).__init__(*args, **kwargs)

    def execute(self, book):
        if book.has_bids() and book.max_bid() <= self.price:
            print("We can match this order")
        else:
            book.add_ask(self)

    
