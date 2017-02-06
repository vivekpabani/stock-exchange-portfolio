# stock-exchange-portfolio
Stock exchange portfolio to simulate buying and selling stocks using stock exchange APIs.

Hosted on:

https://stock-exchange-portfolio.herokuapp.com/

# Functionalities
1. User can search the stock by symbol.
2. User can buy/sell shares by providing quantity.
3. Current postfolio is displayed.
4. Same shares with different buy price are considered different in portfolio.
5. Price recheck is perfomred before transactions
6. Transactions are handled atomically.
7. Recent transaction of latest searched stock is displayed.
8. Since authentication wasn't the priority, simple user login module is provided without password validation.

# Exception Handeling
1. Invalid amount or blank search symbol is handled.
2. User is not allowed to sell what he doesn't have.
3. User is not allowed to buy if he doen't have enough amount.
4. Invalid symbol search is handled.
 
# Build Instructions

    1. Make sure that current directory is stock-exchange-portfolio.
    2. Make sure the database is created, and user is granted proper acccess.
    3. Make sure that stock-exchange/settings file is updated with dababase information.
    
    To Build
    -------------------------------
    make build
    
    
    To Run on Localhost
    -------------------------------    
    make run
    
    
    To Run Tests
    -------------------------------
    make test
    

