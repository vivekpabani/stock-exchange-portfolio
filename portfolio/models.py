from django.db import models

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


class StockQuery(models.Model):

    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=25)
    bid_price = models.DecimalField(max_digits=15, decimal_places=2)
    ask_price = models.DecimalField(max_digits=15, decimal_places=2)


class PortfolioEntry(models.Model):

    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=25)
    buy_price = models.DecimalField(max_digits=15, decimal_places=2)
