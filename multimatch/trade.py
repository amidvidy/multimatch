class Trade(object):
    def __init__(self, symbol, quantity, price, buyer_id, seller_id):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.buyer_id = buyer_id
        self.seller_id = seller_id

    def __repr__(self):
        return "Trade(symbol={0}, quantity={1}, price={2}, buyer_id={3}, seller_id={4})".format(
            self.symbol, self.quantity, self.price, self.buyer_id, self.seller_id)
