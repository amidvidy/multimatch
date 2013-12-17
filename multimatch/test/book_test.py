import unittest

from ..book import OrderBook
from ..orders import LimitBuyOrder, LimitSellOrder

class OrderBookTest(unittest.TestCase):
    
    def setUp(self):
        self.trades = []
        self.book = OrderBook(lambda trade: self.trades.append(trade))

    def numOrdersExecuted(self):
        return len(self.trades)

    def testMatchExact(self):
        sell = LimitSellOrder(100, "BTC/USD", 1, "gavin")
        buy = LimitBuyOrder(100, "BTC/USD", 1, "satoshi")
        self.book.execute(sell)
        self.book.execute(buy)
        self.assertEquals(1, self.numOrdersExecuted(), 
                          "One trade should have been executed")
        [trade] = self.trades
        self.assertEquals(sell.symbol, trade.symbol,
                          "The trade's symbol should be that of the sell order's symbol")
        self.assertEquals(buy.symbol, trade.symbol,
                          "The trade's symbol should be that of the buy order's symbol")
        self.assertEquals(sell.trader_id, trade.seller_id,
                          "The sell order's trader_id should be the seller_id of the trade")
        self.assertEquals(buy.trader_id, trade.buyer_id,
                          "The buy order's trader_id should be the buyer_id of the trade")
        self.assertEquals(sell.quantity, trade.quantity)
        self.assertEquals(buy.quantity, trade.quantity)
        self.assertEquals(sell.price, trade.price)
        self.assertEquals(buy.price, trade.price)

        print(self.book.bids)
        self.assertFalse(self.book.has_bids(), "The book should be empty")
        print(self.book.asks)
        self.assertFalse(self.book.has_asks(), "The book should be empty")
