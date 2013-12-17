import unittest

from ..book import OrderBook
from ..orders import LimitBuyOrder, LimitSellOrder

class OrderBookTest(unittest.TestCase):
    
    def setUp(self):
        self.trades = []
        self.book = OrderBook(lambda trade: self.trades.append(trade))

    def tearDown(self):
        self.book = None

    def numOrdersExecuted(self):
        return len(self.trades)

    def testMatchBuyExact(self):
        sell = LimitSellOrder(100, "BTC/USD", 1, "gavin")
        buy = LimitBuyOrder(100, "BTC/USD", 1, "satoshi")
        
        # Execute Buy Order First
        self.book.execute(buy)
        self.book.execute(sell)
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

        # make sure all the orders were cleared out
        self.assertFalse(self.book.has_bids(), "The book should be empty")
        self.assertFalse(self.book.has_asks(), "The book should be empty")

    def testMatchSellExact(self):
        sell = LimitSellOrder(100, "BTC/USD", 1, "gavin")
        buy = LimitBuyOrder(100, "BTC/USD", 1, "satoshi")

        # Execute Sell Order First
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

        # make sure all the orders were cleared out
        self.assertFalse(self.book.has_bids(), "The book should be empty")
        self.assertFalse(self.book.has_asks(), "The book should be empty")

    def testMatchPartial(self):
        # One seller, multiple buyers. All orders should be matched.
        sell = LimitSellOrder(100, "BTC/USD", 1, "gavin")
        buy1 = LimitBuyOrder(100, "BTC/USD", 0.5, "satoshi")
        buy2 = LimitBuyOrder(100, "BTC/USD", 0.25, "gmaxwell")
        buy3 = LimitBuyOrder(100, "BTC/USD", 0.25, "mhearn")

        # since all orders are for the same price, they should be matched in FIFO Order
        self.book.execute(buy1)
        self.book.execute(buy2)
        self.book.execute(buy3)
        self.book.execute(sell)

        self.assertEquals(3, self.numOrdersExecuted())
        [trade1, trade2, trade3] = self.trades
        self.assertEquals(buy1.quantity, trade1.quantity)
        self.assertEquals(buy1.trader_id, trade1.buyer_id)
        self.assertEquals(buy2.quantity, trade2.quantity)
        self.assertEquals(buy2.trader_id, trade2.buyer_id)
        self.assertEquals(buy3.quantity, trade3.quantity)
        self.assertEquals(buy3.trader_id, trade3.buyer_id)
        

        # make sure all the orders were cleared out
        self.assertFalse(self.book.has_bids(), "The book should be empty")
        self.assertFalse(self.book.has_asks(), "The book should be empty")
