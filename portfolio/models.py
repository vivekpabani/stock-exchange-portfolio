from django.db import models

# Create your models here.


class Stock(models.Model):

    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=25)

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
