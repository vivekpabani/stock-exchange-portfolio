from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from .models import Stock, StockQuery, Portfolio, PortfolioEntry


def home(request):

    username = request.session.get('username', '')

    if not username:
        return redirect('authenticate/login')
    request.username = username
    context = dict()

    if 'symbol' in request.GET:

        print(request.GET['symbol']) 


    return render(request, 'portfolio/home.html', context=context)



def buy_shares(request):

    pass


def sell_shares(request):

    pass
