from django.test import TestCase

# Create your tests here.

from .models import Stock, Portfolio, PortfolioEntry, OrderHistory
from .helper import fetch_json_from_symbol as fetch_json
from .exceptions import (
        StockDoesNotExistException,
        NotEnoughAmountForTransactionException,
        NotEnoughSharesForTransactionException,
        PriceChangedException,
        InternalTransactionException)

from decimal import *

class StockTestCases(TestCase):

    def setUp(self):

        self.found_stock_json = {
                                "AA":{
                                    "symbol": "AA",
                                    "name": "AA Company"
                                 }
                           }
        self.not_found_json = {
                               "null": {
                                  "error": {
                                      "code": 1,
                                      "message": "Unknown symbol."
                                       }
                                   }
                              } 

    def test_from_json_with_found_stock_json(self):

        stock = Stock.from_json(self.found_stock_json)
        self.assertEqual(stock.symbol, self.found_stock_json['AA']['symbol'])
        self.assertEqual(stock.name, self.found_stock_json['AA']['name'])

    def test_from_json_with_not_found_json(self):

        with self.assertRaises(StockDoesNotExistException):
            stock = Stock.from_json(self.not_found_json)


class PortfolioTestCases(TestCase):
    def setUp(self):
        self.portfolio = Portfolio.objects.create(username="Foo") 
        self.stock_aa = {
                        "AA":{
                             "symbol": "AA",
                             "name": "AA Company",
                             "bidPrice": 12.53,
                             "askPrice": 20.24
                             }
                         }

        self.stock_bb = {
                        "BB":{
                             "symbol": "BB",
                             "name": "BB Company",
                             "bidPrice": 25.80,
                             "askPrice": 40.24
                             }
                         }
        self.stock_bb_updated = {
                        "BB":{
                             "symbol": "BB",
                             "name": "BB Company",
                             "bidPrice": 45.80,
                             "askPrice": 70.24
                             }
                         }

        self.stock_query_aa = {
                             "symbol": "AA",
                             "name": "AA Company",
                             "bid_price": 12.53,
                             "ask_price": 20.24
                             }

        self.stock_query_bb = {
                             "symbol": "BB",
                             "name": "BB Company",
                             "bid_price": 25.80,
                             "ask_price": 40.24
                             }
        self.stock_query_bb_updated = {
                             "symbol": "BB",
                             "name": "BB Company",
                             "bid_price": 45.80,
                             "ask_price": 70.24
                             }
    def test_buy_new_stock(self):
        """ check balance """

        symbol = 'AA'
        json = fetch_json(symbol)
        stock_aa = Stock.from_json(json)
        stock_query_aa = {
                         "symbol": symbol,
                         "name": json[symbol]["name"],
                         "bid_price": json[symbol]["bidPrice"] ,
                         "ask_price": json[symbol]["askPrice"] 
                         }
        self.portfolio.buy_shares(stock_query_aa, 1)

        portfolio_entry = PortfolioEntry.objects.filter(username=self.portfolio.username)

        self.assertEqual(len(portfolio_entry), 1)
        self.assertEqual(self.portfolio.amount, Decimal(100000-stock_query_aa['ask_price']).quantize(Decimal('0.00')))
