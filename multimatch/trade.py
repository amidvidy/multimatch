class Trade(object):
    def __init__(self, symbol, quantity, price, buyer_id, seller_id):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.buyer_id = buyer_id
        self.seller_id = seller_id
