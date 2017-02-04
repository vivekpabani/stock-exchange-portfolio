from django.db import models, transaction, IntegrityError
from decimal import* 

# Create your models here.


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
            print("Stock Not Available")
            return None

        stock, created = Stock.objects.get_or_create(symbol=symbol)

        if created:

            stock.name = in_json[symbol]['name']
            if not stock.name:
                stock.name = symbol
            stock.save()

        print("Stock Returning : ", stock.name)
        return stock 

    def __str__(self):

        return self.symbol + ' : ' + self.name


class Portfolio(models.Model):

    username = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=15,
                                 decimal_places=2,
                                 default=100000.00) 

    def buy_shares(self, stock_query, quantity):
        stock = Stock.objects.get(symbol = stock_query['symbol'])
        buy_price = Decimal.from_float(stock_query['ask_price']).quantize(Decimal('0.00'))

        # Check if the amount is enough

        buy_amount = (buy_price * quantity).quantize(Decimal('0.00'))

        if buy_amount > self.amount:

            # throw an error here later.  
            print("You don't have enough amount to make this transaction.")
            return

        try:
            with transaction.atomic():
                print("In atomic")
                self.amount = self.amount - buy_amount
                self.save() 
                print("self saved")

                print(self.username, stock.symbol, buy_price)

                portfolio_entry = PortfolioEntry.objects.filter(
                                            username=self.username,
                                            stock=stock,
                                            buy_price=buy_price)

                print("Before protfoio if")
                if portfolio_entry:
                    "In portfolio entry"
                    portfolio_entry = portfolio_entry[0]
                    portfolio_entry.quantity = portfolio_entry.quantity + quantity
                    portfolio_entry.save()
                else:
                    PortfolioEntry.objects.create( 
                                           username=self.username,
                                           stock=stock,
                                           buy_price=buy_price,
                                           quantity=quantity)
                print("after protfoio if")
            
        except IntegrityError:
            pass


    def sell_shares(self, stock_query, quantity):

        stock = Stock.objects.get(symbol = stock_query['symbol'])
        sell_price = Decimal.from_float(stock_query['bid_price']).quantize(Decimal('0.00'))

        portfolio_entries = PortfolioEntry.objects.filter(
                                         username=self.username,
                                         stock=stock).order_by('-buy_price')
        available_quantity = 0

        if portfolio_entries:  
            available_quantity = sum(entry.quantity for entry in portfolio_entries)

        if available_quantity < quantity:
         
            # throw an error here later.
            print("You don't have enough shares to make this transaction.")
            return

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

        except IntegrityError:
            pass


class StockQuery(models.Model):
 
    stock = models.ForeignKey('portfolio.Stock')
    #name = models.CharField(max_length=200)
    #symbol = models.CharField(max_length=25)
    bid_price = models.DecimalField(max_digits=15, decimal_places=2)
    ask_price = models.DecimalField(max_digits=15, decimal_places=2)


class PortfolioEntry(models.Model):
    username = models.CharField(max_length=20) 
    stock = models.ForeignKey('portfolio.Stock')
    buy_price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.IntegerField()
