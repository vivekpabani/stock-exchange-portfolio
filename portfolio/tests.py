from django.test import TestCase

# Create your tests here.

from .models import Stock, Portfolio, PortfolioEntry, OrderHistory
from .exceptions import (
        StockDoesNotExistException,
        NotEnoughAmountForTransactionException,
        NotEnoughSharesForTransactionException,
        InternalTransactionException)

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
        


    def test_buy_new_stock(self):
	""" check balance """
		
		pass
		
	def test_buy_existing_stock(self):
		pass
		
	def test_sell_stock(self):
		""" check balance update, quantity changed"""
		pass
		
	def test_sell_stocks_now_none_left(self):
		""" make sure removed from portfolio """
		pass
		
	def test_sell_stock_do_not_own(self):
		pass
		
	def test_buy_negative_stocks(self):
		pass
		
	def test_sell_negative_stocks(self):
		pass
		
	def lookup_valid_symbol(self):
		pass
	
	def lookup_invalid_symbol(self):
		pass
