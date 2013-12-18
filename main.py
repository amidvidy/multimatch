from __future__ import print_function

from multimatch.log import get_logger
from multimatch.asset import make_symbol
from multimatch.multi import MultiBook
from multimatch.orders import LimitBuyOrder, LimitSellOrder, MarketBuyOrder

logger = get_logger(__name__)

def run_orders(book, symbol):
    logger.info("Running orders with symbol {0}, book {1}".format(symbol, book))
    o1 = LimitSellOrder(100, symbol, 5, "bill")
    o2 = LimitSellOrder(101, symbol, 0.5, "ted")
    o3 = LimitBuyOrder(99, symbol, 10, "chris")
    o4 = LimitBuyOrder(98, symbol, 20, "susan")
    book.execute(o1)
    book.execute(o2)
    book.execute(o3)
    book.execute(o4)
    logger.info(book.quote(symbol))
    logger.info(book.quote(symbol))
    m = MarketBuyOrder(symbol, 5.3, "dogge")
    book.execute(m)
    logger.info(book.quote(symbol))

def main():
    logger.info("Creating MultiBook")
    book = MultiBook()
    btcusd = make_symbol("BTC", "USD")
    run_orders(book, btcusd)


if __name__ == '__main__':
    main()
