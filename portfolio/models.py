from django.db import models

# Create your models here.


class Stock(models.Model):

    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=25)

    def __str__(self):

        return self.symbol + ' : ' + self.name

