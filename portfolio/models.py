from django.db import models, transaction, IntegrityError

from decimal import * 
from datetime import datetime
from django.utils import timezone
from .exceptions import (
        StockDoesNotExistException,
        NotEnoughAmountForTransactionException,
        NotEnoughSharesForTransactionException,
        PriceChangedException,
        InternalTransactionException)
from .helper import fetch_json_from_symbol as fetch_json

class Stock(models.Model):
    """
    This class represents the stock object with minimal attributes.
    It can be created from json or by calling the constructor. 
    """
    
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
    """
    This class represents the user's portfolio or the account.
    It has username and the amount of the portfolio.
    This provides the functions of buying and selling shares.
    """

    username = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=15,
                                 decimal_places=2,
                                 default=100000.00) 

    def buy_shares(self, stock_query, quantity):
        """
        Buy the shares of given uantity based on values in stock_query.
        Verify if current price matches, and enough balance available. 

        :param stock_query (dict): a dictionary object with details about the stock.
        :param quantity (int): quantity to buy 
        """

        # verify if price changed since query.

        symbol = stock_query['symbol']
        latest_buy_price = fetch_json(symbol)[symbol]['askPrice']

        if latest_buy_price != stock_query['ask_price']:
            raise PriceChangedException("The price of the stock changed. Please try again.")
        
        stock = Stock.objects.get(symbol = stock_query['symbol'])

        buy_price = Decimal.from_float(stock_query['ask_price']).quantize(Decimal('0.00'))

        # Check if the amount is enough

        buy_amount = (buy_price * quantity).quantize(Decimal('0.00'))

        if buy_amount > self.amount:
            raise NotEnoughAmountForTransactionException("You don't have enough amount to make this transaction.")

        try:
            # update amount
            # insert/update the portfolio entry
            # update order history

            with transaction.atomic():
                self.amount = Decimal(self.amount) - buy_amount
                self.save() 

                # search for portfolio entry of same stock with same price
                # if found, update the quantity
                # else insert new record

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

        # verify if price changed since query.

        symbol = stock_query['symbol']

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
        """
        Reset the portfolio by deleting all portfolio entries, order history and default amount.
        """

        PortfolioEntry.objects.filter(username=self.username).delete()
        OrderHistory.objects.filter(username=self.username).delete()
        self.amount = Decimal(100000.00)
        self.save()


class PortfolioEntry(models.Model):
    """
    This class represents the entry in portfolio per shares available 
    unique by stock and buy_price combined.
    """

    username = models.CharField(max_length=20) 
    stock = models.ForeignKey('portfolio.Stock')
    buy_price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.IntegerField()


class OrderHistory(models.Model):
    """
    This class represents order history. It has one line per order.
    """

    ORDER_TYPE_CHOICES = (('BUY', 'BUY'),
                          ('SELL', 'SELL'),
                         ) 
    username = models.CharField(max_length=20)
    stock = models.ForeignKey('portfolio.Stock')
    price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.IntegerField()
    datetime = models.DateTimeField(default=timezone.now)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES) 
