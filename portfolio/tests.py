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

        self.available_stock_symbol = 'A'
        self.not_available_stock_symbol = 'BBBBB'

    def test_from_json_with_found_stock_json(self):

        found_stock_json = fetch_json(self.available_stock_symbol)
        stock = Stock.from_json(found_stock_json)
        self.assertEqual(stock.symbol, self.available_stock_symbol)
        self.assertEqual(stock.name, found_stock_json[self.available_stock_symbol]['name'])

    def test_from_json_with_not_found_json(self):

        not_found_json = fetch_json(self.not_available_stock_symbol)
        with self.assertRaises(StockDoesNotExistException):
            stock = Stock.from_json(not_found_json)


class PortfolioTestCases(TestCase):

    def setUp(self):
        self.portfolio = Portfolio.objects.create(username="Foo") 
        self.symbol_a = "A"
        self.symbol_b = "B"

    def test_buy_one_new_stock(self):

        json = fetch_json(self.symbol_a)
        stock_a = Stock.from_json(json)
        stock_query_a = self.json_to_query(json)

        self.portfolio.buy_shares(stock_query_a, 1)

        portfolio_entries = PortfolioEntry.objects.filter(username=self.portfolio.username)
        entry = portfolio_entries[0] 

        self.assertEqual(len(portfolio_entries), 1)
        self.assertEqual(self.portfolio.amount, Decimal(100000-stock_query_a['ask_price']).quantize(Decimal('0.00')))
        self.assertEqual(entry.stock, stock_a)
        self.assertEqual(entry.quantity, 1)

    def test_buy_multiple_new_stocks(self):

        json = fetch_json(self.symbol_a)
        stock_a = Stock.from_json(json)
        stock_query_a = self.json_to_query(json)

        # buy first share of stock_a
        self.portfolio.buy_shares(stock_query_a, 1)

        portfolio_entries = PortfolioEntry.objects.filter(username=self.portfolio.username)
        entry = portfolio_entries[0]

        self.assertEqual(len(portfolio_entries), 1)
        self.assertEqual(self.portfolio.amount, Decimal(100000-stock_query_a['ask_price']).quantize(Decimal('0.00')))
        self.assertEqual(entry.stock, stock_a)
        self.assertEqual(entry.quantity, 1)

        # buy second share of stock_b
        json = fetch_json(self.symbol_b)
        stock_b = Stock.from_json(json)
        stock_query_b = self.json_to_query(json)
        self.portfolio.buy_shares(stock_query_b, 1)

        portfolio_entries = PortfolioEntry.objects.filter(username=self.portfolio.username).order_by('id')

        self.assertEqual(len(portfolio_entries), 2)
        self.assertEqual(self.portfolio.amount, Decimal(100000-stock_query_a['ask_price']-stock_query_b['ask_price']).quantize(Decimal('0.00')))

        self.assertEqual(portfolio_entries[0].stock, stock_a)
        self.assertEqual(portfolio_entries[0].quantity, 1)

        self.assertEqual(portfolio_entries[1].stock, stock_b)
        self.assertEqual(portfolio_entries[1].quantity, 1)

    def test_buy_existing_stock(self):

        json = fetch_json(self.symbol_a)
        stock_a = Stock.from_json(json)
        stock_query_a = self.json_to_query(json)

        # buy first share of stock_a
        self.portfolio.buy_shares(stock_query_a, 1)

        portfolio_entries = PortfolioEntry.objects.filter(username=self.portfolio.username)
        entry = portfolio_entries[0] 

        self.assertEqual(len(portfolio_entries), 1)
        self.assertEqual(self.portfolio.amount, Decimal(100000-stock_query_a['ask_price']).quantize(Decimal('0.00')))
        self.assertEqual(entry.stock, stock_a)
        self.assertEqual(entry.quantity, 1)

        # buy second share of stock_a
        self.portfolio.buy_shares(stock_query_a, 1)

        portfolio_entries = PortfolioEntry.objects.filter(username=self.portfolio.username)
        entry = portfolio_entries[0]

        self.assertEqual(len(portfolio_entries), 1)
        self.assertEqual(self.portfolio.amount, Decimal(100000-2*stock_query_a['ask_price']).quantize(Decimal('0.00')))
        self.assertEqual(entry.stock, stock_a)
        self.assertEqual(entry.quantity, 2)

    def test_buy_stock_updated_price_inbetween(self):

        json = fetch_json(self.symbol_a)
        stock_a = Stock.from_json(json)
        stock_query_a = self.json_to_query(json)

        # mock updated price inbetween
        stock_query_a['ask_price'] += 5.0

        with self.assertRaises(PriceChangedException):
            self.portfolio.buy_shares(stock_query_a, 1)

    def test_sell_stock_available_quantity(self):

        json = fetch_json(self.symbol_a)
        stock_a = Stock.from_json(json)
        stock_query_a = self.json_to_query(json)

        self.portfolio.buy_shares(stock_query_a, 1)

        portfolio_entries = PortfolioEntry.objects.filter(username=self.portfolio.username)
        entry = portfolio_entries[0]

        self.assertEqual(len(portfolio_entries), 1)
        self.assertEqual(self.portfolio.amount, Decimal(100000-stock_query_a['ask_price']).quantize(Decimal('0.00')))
        self.assertEqual(entry.stock, stock_a)
        self.assertEqual(entry.quantity, 1)

        self.portfolio.sell_shares(stock_query_a, 1)

        portfolio_entries = PortfolioEntry.objects.filter(username=self.portfolio.username)

        self.assertEqual(len(portfolio_entries), 0)
        self.assertEqual(self.portfolio.amount, Decimal(100000-stock_query_a['ask_price']+stock_query_a['bid_price']).quantize(Decimal('0.00')))

    def json_to_query(self, stock):

        stock_query = dict()
        key = list(stock.keys())[0]
        if key == "null":
            return -1

        stock_query['symbol'] = key
        stock_query['name'] = stock[key]['name']
        stock_query['bid_price'] = stock[key]['bidPrice']
        stock_query['ask_price'] = stock[key]['askPrice']

        return stock_query
