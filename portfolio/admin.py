from django.contrib import admin

# Register your models here.

from .models import Stock, Portfolio, PortfolioEntry, OrderHistory 

admin.site.register(Stock)
admin.site.register(Portfolio)
admin.site.register(PortfolioEntry)
admin.site.register(OrderHistory)
