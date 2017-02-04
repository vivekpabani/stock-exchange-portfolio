from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages 

from decimal import *

from .models import Stock, StockQuery, Portfolio, PortfolioEntry
from .helper import fetch_json_from_symbol as fetch_json
from .forms import TransactionForm, SearchSymbolForm

def home(request):

    username = request.session.get('username', '')

    if not username:
        return redirect('authenticate/login')

    request.username = username
    portfolio, created = Portfolio.objects.get_or_create(username=username)
    portfolio_entries = PortfolioEntry.objects.filter(username=username)

    context = dict()
    context['portfolio'] = portfolio
    if portfolio_entries:
        context['portfolio_entries'] = portfolio_entries

    if 'stock_query' in request.session.keys():
        context['stock_query'] = request.session['stock_query']

    transaction_form = TransactionForm(request.POST or None)
    search_symbol_form = SearchSymbolForm(request.POST or None)
    context['transaction_form'] = transaction_form
    context['search_symbol_form'] = search_symbol_form 

    if 'symbol' in request.GET:
        symbol = request.GET['symbol'] 
        json = fetch_json(symbol)
        stock = Stock.from_json(json)
        stock_query = {'symbol':symbol,
                       'name':stock.name,
                       'bid_price':json[symbol]['bidPrice'],
                       'ask_price':json[symbol]['askPrice']}
        request.session['stock_query'] = stock_query

        context['stock_query'] = stock_query

    return render(request, 'portfolio/home.html', context)


def transaction(request):

    messages.warning(request, "Starting transaction")

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
    PortfolioEntry.objects.filter(username=username).delete()
    portfolio = Portfolio.objects.get(username=username)
    #setattr(portfolio, amount, amount.default) 
    portfolio.amount = Decimal(100000.00)
    portfolio.save()
    request.session['stock_query'] = ''

    return redirect(reverse("portfolios:home"))
