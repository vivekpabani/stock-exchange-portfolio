from django.db import models, transaction

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

        if 'symbol' not in in_json:
            print("Stock Not Available")
            return None

        stock, created = Stock.objects.get_or_create(symbol=in_json['symbol'])

        if created:

            stock['name'] = in_json['name']
            stock.save()

        return stock 

    def __str__(self):

        return self.symbol + ' : ' + self.name


class Portfolio(models.Model):

    username = models.CharField(max_length=20)
    amount = models.DecimalField(min_value=0, 
                                 max_digits=15, 
                                 decimal_places=2, 
                                 default_value=100000.00)

    def buy_stock(self, query_stock, quantity):

        stock = stock_query.stock
        buy_price = stock_query.bid_price

        # Check if the amount is enough

        buy_amount = buy_price * quantity

        if buy_amount > buy_price:

            # throw an error here later.  
            print("You don't have enough amount to make this transaction.")
            return

        try:
            with transaction.atomic():
                self.amount = self.amount - buy_amount
                self.save() 

                portfolio_entry = PortfolioEntry.objects.filter(
                                            username=request.username,
                                            stock=stock,
                                            buy_price=price)

                if portfolio_entry:
                    portfolio_entry.quantity = portfolio_entry.quantity + quantity
                    portfolio_entry.save()
                else:
                    PortfolioEntry.objects.create( 
                                           username=request.username,
                                           stock=stock,
                                           buy_price=price,
                                           quantity=quantity)
            
        except IntegrityError:
            pass


    def sell_stock(self, query_stock, quantity):

        stock = stock_query.stock
        sell_price = stock_query.bid_price

        portfolio_entries = PortfolioEntry.objects.filter(
                                         username=request.username,
                                         stock=stock).order_by('-buy_price')
        available_quantity = 0

        if portfolio_entries:  
            available_quantity = sum(portfolio_entries, key=lambda entry:entry.quantity)

        if available_quantity < quantity:
         
            # throw an error here later.
            print("You don't have enough shares to make this transaction.")
            return

        try:
            with transaction.atomic():

                remaining_quantity = quantity

                for entry in portfolio_entries:
                    if entry.quantity < remaining_quantity:
                        remaining_quantity = remaining_quantity - entry.quantity
                        entry.delete()
                    else:
                        entry.quantity = entry.quantity - remaining_quantity
                        entry.save()
                        break

                self.amount = self.amount + sell_price*quantity

        except IntegrityError:
            pass


class StockQuery(models.Model):
 
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=25)
    bid_price = models.DecimalField(max_digits=15, decimal_places=2)
    ask_price = models.DecimalField(max_digits=15, decimal_places=2)


class PortfolioEntry(models.Model):
    user_name = models.CharField(max_length=20) 
    stock = models.ForeignKey('portfolio.Stock')
    buy_price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.IntegerField(min_value=1)
