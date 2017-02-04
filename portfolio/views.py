from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages 
from django.core.exceptions import ValidationError

from decimal import *

from .models import Stock, Portfolio, PortfolioEntry, OrderHistory
from .helper import fetch_json_from_symbol as fetch_json
from .forms import TransactionForm, SearchSymbolForm

def home(request):

    username = request.session.get('username', '')

    if not username:
        return redirect('authenticate/login')

    request.username = username
    
    order_history = None
    context = dict()

    if 'stock_query' in request.session.keys() and request.session['stock_query']:
        stock_query = request.session['stock_query']
        context['stock_query'] = stock_query
        symbol = stock_query['symbol'] 
        stock = Stock.objects.get(symbol=symbol)
        order_history = OrderHistory.objects.filter(username=username, 
                                                    stock=stock).order_by('-id')[:5]

    if 'symbol' in request.GET:
        if not request.GET['symbol']:
            raise ValidationError("No symbol found. Please try again.")
        symbol = request.GET['symbol'] 
        json = fetch_json(symbol)
        stock = Stock.from_json(json)
        stock_query = {'symbol':symbol,
                       'name':stock.name,
                       'bid_price':json[symbol]['bidPrice'],
                       'ask_price':json[symbol]['askPrice']}
        request.session['stock_query'] = stock_query

        context['stock_query'] = stock_query

        order_history = OrderHistory.objects.filter(username=username, 
                                                    stock=stock).order_by('-id')[:5]

    portfolio, created = Portfolio.objects.get_or_create(username=username)

    portfolio_entries = PortfolioEntry.objects.filter(username=username)
    portfolio_entries = sorted(portfolio_entries, key= lambda entry: entry.stock.name)

    transaction_form = TransactionForm(request.POST or None)
    search_symbol_form = SearchSymbolForm(request.POST or None)

    context['portfolio'] = portfolio
    context['username'] = username
    context['transaction_form'] = transaction_form
    context['search_symbol_form'] = search_symbol_form

    if order_history:
        context['order_history'] = order_history 

    if portfolio_entries:
        context['portfolio_entries'] = portfolio_entries

    return render(request, 'portfolio/home.html', context)


def transaction(request):

    portfolio = Portfolio.objects.get(username=request.session['username'])
    stock_query = request.session['stock_query']
    quantity = request.POST['quantity']    

    if 'buy' in request.POST:
        print("Buy In POST")
        portfolio.buy_shares(stock_query, int(quantity))
    elif 'sell' in request.POST:
        portfolio.sell_shares(stock_query, int(quantity))

    return redirect(reverse("portfolios:home"))


def reset(request):

    username=request.session['username']
    portfolio = Portfolio.objects.get(username=username)
    portfolio.reset()
    request.session['stock_query'] = ''

    return redirect(reverse("portfolios:home"))
