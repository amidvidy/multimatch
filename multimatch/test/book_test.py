import unittest

from ..book import OrderBook
from ..orders import LimitBuyOrder, LimitSellOrder
from ..asset import make_symbol

class OrderBookTest(unittest.TestCase):
    
    def setUp(self):
        self.trades = []
        self.book = OrderBook(lambda trade: self.trades.append(trade))

    def tearDown(self):
        self.book = None
        self.trades = None

    def numOrdersExecuted(self):
        return len(self.trades)

    def testMatchBuyExact(self):
        sell = LimitSellOrder(100, make_symbol('BTC', 'USD'), 1, 'gavin')
        buy = LimitBuyOrder(100, make_symbol('BTC', 'USD'), 1, 'satoshi')
        
        # Execute Buy Order First
        self.book.execute(buy)
        self.book.execute(sell)
        self.assertEquals(1, self.numOrdersExecuted(), 
                          'One trade should have been executed')
        [trade] = self.trades
        self.assertEquals(sell.symbol, trade.symbol,
                          'The trade\'s symbol should be that of the sell order\'s symbol')
        self.assertEquals(buy.symbol, trade.symbol,
                          'The trade\'s symbol should be that of the buy order\'s symbol')
        self.assertEquals(sell.trader_id, trade.seller_id,
                          'The sell order\'s trader_id should be the seller_id of the trade')
        self.assertEquals(buy.trader_id, trade.buyer_id,
                          'The buy order\'s trader_id should be the buyer_id of the trade')
        self.assertEquals(sell.quantity, trade.quantity)
        self.assertEquals(buy.quantity, trade.quantity)
        self.assertEquals(sell.price, trade.price)
        self.assertEquals(buy.price, trade.price)

        # make sure all the orders were cleared out
        self.assertFalse(self.book.has_bids(), 'The book should be empty')
        self.assertFalse(self.book.has_asks(), 'The book should be empty')

    def testMatchSellExact(self):
        sell = LimitSellOrder(100, 'BTC/USD', 1, 'gavin')
        buy = LimitBuyOrder(100, 'BTC/USD', 1, 'satoshi')

        # Execute Sell Order First
        self.book.execute(sell)
        self.book.execute(buy)
        self.assertEquals(1, self.numOrdersExecuted(), 
                          'One trade should have been executed')
        [trade] = self.trades
        self.assertEquals(sell.symbol, trade.symbol,
                          'The trade\'s symbol should be that of the sell order\'s symbol')
        self.assertEquals(buy.symbol, trade.symbol,
                          'The trade\'s symbol should be that of the buy order\'s symbol')
        self.assertEquals(sell.trader_id, trade.seller_id,
                          'The sell order\'s trader_id should be the seller_id of the trade')
        self.assertEquals(buy.trader_id, trade.buyer_id,
                          'The buy order\'s trader_id should be the buyer_id of the trade')
        self.assertEquals(sell.quantity, trade.quantity)
        self.assertEquals(buy.quantity, trade.quantity)
        self.assertEquals(sell.price, trade.price)
        self.assertEquals(buy.price, trade.price)

        # make sure all the orders were cleared out
        self.assertFalse(self.book.has_bids(), 'The book should be empty')
        self.assertFalse(self.book.has_asks(), 'The book should be empty')

    def testMatchPartial(self):
        # One seller, multiple buyers. All orders should be matched.
        sell = LimitSellOrder(100, make_symbol('BTC', 'USD'), 1, 'gavin')
        buy1 = LimitBuyOrder(100, make_symbol('BTC', 'USD'), 0.5, 'satoshi')
        buy2 = LimitBuyOrder(100, make_symbol('BTC', 'USD'), 0.25, 'gmaxwell')
        buy3 = LimitBuyOrder(100, make_symbol('BTC', 'USD'), 0.25, 'mhearn')

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
        self.assertFalse(self.book.has_bids(), 'The book should be empty')
        self.assertFalse(self.book.has_asks(), 'The book should be empty')

    def testMatchBuyPartialUnfilled(self):
        # One seller, one buyer. Buyer should be filled, seller should be partially filled
        # price should be the sellers since it was on the book first
        
        sell = LimitSellOrder(100, make_symbol('BTC', 'USD'), 1, 'gavin')
        buy = LimitBuyOrder(150, make_symbol('BTC', 'USD'), 0.25, 'satoshi')

        self.book.execute(sell)
        self.book.execute(buy)

        self.assertEquals(1, self.numOrdersExecuted())
        [trade] = self.trades
        self.assertEquals(make_symbol('BTC', 'USD'), trade.symbol)
        self.assertEquals(buy.quantity, trade.quantity)
        self.assertEquals(buy.trader_id, trade.buyer_id)
        self.assertEquals(sell.trader_id, trade.seller_id)
        # Order should be filled at the sellers price since it was on the book first
        self.assertEquals(sell.price, trade.price)

        self.assertTrue(self.book.has_asks(), 'There should still be an ask on the book')

        self.assertFalse(self.book.has_bids(), 'There should be no bids')

    def testMatchLimitSellPriceOrder(self):
        # when matching a limit order, the trade executes at the price of the order
        # that was on the book, not the new order

        # See: http://money.stackexchange.com/questions/15156/how-do-exchanges-match-limit-orders

        # gavin posts an order to buy 5 BTC @ 100 USD each
        self.book.execute(LimitBuyOrder(100, make_symbol('BTC', 'USD'), 5, 'gavin'))
        # satoshi posts an order to buy 10 BTC @ 99 USD each
        self.book.execute(LimitBuyOrder(99, make_symbol('BTC', 'USD'), 10, 'satoshi'))
        # mhearn posts an order to buy 20 BTC @ 50 USD each
        self.book.execute(LimitBuyOrder(50, make_symbol('BTC', 'USD'), 20, 'mhearn'))

        # finally, we execute a limit order to sell 100BTC at 0.01 USD
        self.book.execute(LimitSellOrder(0.01, make_symbol('BTC', 'USD'), 100, 'fool'))

        # all 3 buys should have been filled
        self.assertEquals(3, self.numOrdersExecuted())
        [gavin_trade, satoshi_trade, hearn_trade] = self.trades

        # gavin's order should have been filled first at a price of 100
        self.assertEquals('gavin', gavin_trade.buyer_id)
        self.assertEquals(100, gavin_trade.price)

        # satoshi's order should have been filled second at a price of 99
        self.assertEquals('satoshi', satoshi_trade.buyer_id)
        self.assertEquals(99, satoshi_trade.price)

        # mhearns order should have been filled last at a price of 50
        self.assertEquals('mhearn', hearn_trade.buyer_id)
        self.assertEquals(50, hearn_trade.price)

        # All the bids should have been filled
        self.assertFalse(self.book.has_bids())
        # Partial order should still be on the book
        self.assertTrue(self.book.has_asks())

    def testMatchLimitBuyPriceOrder(self):
        # same as above, but for the opposite situation

        # gavin posts an order to sell 5 BTC @ 100 USD each
        self.book.execute(LimitSellOrder(100, make_symbol('BTC', 'USD'), 5, 'gavin'))
        # satoshi posts an order to sell 10 BTC @ 99 USD each
        self.book.execute(LimitSellOrder(99, make_symbol('BTC', 'USD'), 10, 'satoshi'))
        # mhearn posts an order to sell 20 BTC @ 50 USD each
        self.book.execute(LimitSellOrder(50, make_symbol('BTC', 'USD'), 20, 'mhearn'))

        # finally, we execute a limit order to buy 100BTC at 1000 USD
        self.book.execute(LimitBuyOrder(1000, make_symbol('BTC', 'USD'), 100, 'fool'))

        # all 3 buys should have been filled
        self.assertEquals(3, self.numOrdersExecuted())
        [hearn_trade, satoshi_trade, gavin_trade] = self.trades

        # mhearns order should have been filled first at a price of 50
        self.assertEquals('mhearn', hearn_trade.seller_id)
        self.assertEquals(50, hearn_trade.price)

        # satoshi's order should have been filled second at a price of 99
        self.assertEquals('satoshi', satoshi_trade.seller_id)
        self.assertEquals(99, satoshi_trade.price)
        
        # gavin's order should have been filled last at a price of 100
        self.assertEquals('gavin', gavin_trade.seller_id)
        self.assertEquals(100, gavin_trade.price)

        # All the asks should have been filled
        self.assertFalse(self.book.has_asks())
        # Partial buy order should still be on the book
        self.assertTrue(self.book.has_bids())
    
