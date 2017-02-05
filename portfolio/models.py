from django.db import models, transaction, IntegrityError

from decimal import * 
from datetime import datetime
from .exceptions import (
        StockDoesNotExistException,
        NotEnoughAmountForTransactionException,
        NotEnoughSharesForTransactionException,
        PriceChangedException,
        InternalTransactionException)
from .helper import fetch_json_from_symbol as fetch_json

class Stock(models.Model):
    
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=25)

    @staticmethod
    def from_json(in_json):
        """
        A static method to create an instance of stock with the inputs from json
        retrieved using api. 

        :param in_json (json): stock data in json format retrieved by api

        :return (Stock): an instance of Stock class with attributes from json.
        """

        symbol = list(in_json.keys())[0]

        if symbol == "null":
            raise StockDoesNotExistException("Cannot find any stock with given symbol.")

        stock, created = Stock.objects.get_or_create(symbol=symbol)

        if created:

            stock.name = in_json[symbol]['name']
            if not stock.name:
                stock.name = symbol
            stock.save()

        return stock 


class Portfolio(models.Model):

    username = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=15,
                                 decimal_places=2,
                                 default=100000.00) 

    def buy_shares(self, stock_query, quantity):
        symbol = stock_query['symbol']
        latest_buy_price = fetch_json(symbol)[symbol]['askPrice']
        if latest_buy_price != stock_query['ask_price']:
            raise PriceChangedException("The price of the stock changed. Please try again.")
        stock = Stock.objects.get(symbol = stock_query['symbol'])
        buy_price = Decimal.from_float(stock_query['ask_price']).quantize(Decimal('0.00'))
        latest_buy_price = fetch_json(stock.symbol)[stock.symbol]['askPrice']

        # Check if the amount is enough

        buy_amount = (buy_price * quantity).quantize(Decimal('0.00'))

        if buy_amount > self.amount:
            raise NotEnoughAmountForTransactionException("You don't have enough amount to make this transaction.")

        try:
            with transaction.atomic():
                self.amount = self.amount - buy_amount
                self.save() 

                portfolio_entry = PortfolioEntry.objects.filter(
                                            username=self.username,
                                            stock=stock,
                                            buy_price=buy_price)

                if portfolio_entry:
                    portfolio_entry = portfolio_entry[0]
                    portfolio_entry.quantity = portfolio_entry.quantity + quantity
                    portfolio_entry.save()
                else:
                    PortfolioEntry.objects.create( 
                                           username=self.username,
                                           stock=stock,
                                           buy_price=buy_price,
                                           quantity=quantity)

                OrderHistory.objects.create(
                                           username=self.username,
                                           stock=stock,
                                           price=buy_price,
                                           quantity=quantity,
                                           order_type="BUY")
            
        except IntegrityError:
            raise InternalTransactionException("Internal transaction error. Please try again.")


    def sell_shares(self, stock_query, quantity):

        latest_sell_price = fetch_json(symbol)[symbol]['bidPrice']
        if latest_sell_price != stock_query['bid_price']:
            raise PriceChangedException("The price of the stock changed. Please try again.")

        stock = Stock.objects.get(symbol = stock_query['symbol'])
        sell_price = Decimal.from_float(stock_query['bid_price']).quantize(Decimal('0.00'))

        portfolio_entries = PortfolioEntry.objects.filter(
                                         username=self.username,
                                         stock=stock).order_by('-buy_price')
        available_quantity = 0

        if portfolio_entries:  
            available_quantity = sum(entry.quantity for entry in portfolio_entries)

        if available_quantity < quantity:
         
            raise NotEnoughSharesForTransactionException("You don't have enough shares to make this transaction.")

        try:
            with transaction.atomic():

                remaining_quantity = quantity

                for entry in portfolio_entries:
                    if entry.quantity <= remaining_quantity:
                        remaining_quantity = remaining_quantity - entry.quantity
                        entry.delete()
                    else:
                        entry.quantity = entry.quantity - remaining_quantity
                        entry.save()
                        break

                self.amount = self.amount + (sell_price*quantity).quantize(Decimal('0.00'))
                self.save()

                OrderHistory.objects.create(
                                           username=self.username,
                                           stock=stock,
                                           price=sell_price,
                                           quantity=quantity,
                                           order_type="SELL")

        except IntegrityError:
            raise InternalTransactionException("Internal transaction error. Please try again.")

    def reset(self):

        PortfolioEntry.objects.filter(username=self.username).delete()
        OrderHistory.objects.filter(username=self.username).delete()
        self.amount = Decimal(100000.00)
        self.save()


class PortfolioEntry(models.Model):
    username = models.CharField(max_length=20) 
    stock = models.ForeignKey('portfolio.Stock')
    buy_price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.IntegerField()

class OrderHistory(models.Model):

    ORDER_TYPE_CHOICES = (('BUY', 'BUY'),
                          ('SELL', 'SELL'),
                         ) 
    username = models.CharField(max_length=20)
    stock = models.ForeignKey('portfolio.Stock')
    price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.IntegerField()
    datetime = models.DateTimeField(default=datetime.now)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES) 
