from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from .models import Stock, StockQuery, Portfolio, PortfolioEntry
from .helper import fetch_json_from_symbol as fetch_json

def home(request):

    username = request.session.get('username', '')

    if not username:
        return redirect('authenticate/login')

    request.username = username
    portfolio, created = Portfolio.objects.get_or_create(username=username)
    portfolio_entries = PortfolioEntry.objects.filter(username=username)

    context = dict()
    print(portfolio, portfolio.username, portfolio.amount)
    context['portfolio'] = portfolio
    if portfolio_entries:
        context['portfolio_entries'] = portfolio_entries

    if 'stock_query' in request.session.keys():
        context['stock_query'] = request.session['stock_query']

    if 'symbol' in request.GET:
        symbol = request.GET['symbol'] 
        json = fetch_json(symbol)
        stock = Stock.from_json(json)
        stock_query = {'symbol':symbol,
                       'name':stock.name,
                       'bid_price':json[symbol]['bidPrice'],
                       'ask_price':json[symbol]['askPrice']}
        """
        stock_query = StockQuery.objects.create(stock=stock,
                                                bid_price=json[symbol]['bidPrice'],
                                                ask_price=json[symbol]['askPrice'])


        request.session['stock_symbol'] = symbol
        request.session['stock_bid_price'] = stock_query.bid_price 
        request.session['stock_ask_price'] = stock_query.ask_price
        """
        request.session['stock_query'] = stock_query

        context['stock_query'] = stock_query

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


def buy_shares(request):

    print("In Buy")
    print(request.session['username'])
    portfolio = Portfolio.objects.get(username=request.session['username'])

    """
    stock = Stock.objects.get(symbol=request.session['stock_symbol'])
    stock_query = StockQuery.objects.create(stock=stock,
                                            bid_price=request.session['stock_bid_price'],
                                            ask_price=request.session['stock_ask_price'])
    """
    stock_query = request.session['stock_query']
    quantity = request.POST['quantity']

    print("Before buy")
    print(quantity, portfolio.username, stock_query['bid_price'])
    portfolio.buy_shares(stock_query, int(quantity)) 
    print("Buy Done")

    return redirect(reverse("portfolios:home"))


def sell_shares(request):

    pass
