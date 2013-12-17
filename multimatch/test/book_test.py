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
        buy = LimitBuyOrder("BTC/USD", 1, 100)
        sell = LimitSellOrder("BTC/USD", 1, 100)
        self.book.execute(buy)
        self.book.execute(sell)
        self.assertEquals(1, self.numOrdersExecuted(), "One order should have been executed")
