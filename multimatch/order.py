class Order(object):
    def __init__(self, symbol, type, quantity, price, *args, **kwargs):
        self.symbol = symbol
        self.type = type
        self.quantity = quantity
        self.price = price
