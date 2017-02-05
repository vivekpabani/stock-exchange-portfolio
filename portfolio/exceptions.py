
class StockDoesNotExistException(Exception):
    pass

class NotEnoughAmountForTransactionException(Exception):
    pass

class NotEnoughSharesForTransactionException(Exception):
    pass

class CannotConnectToServerException(Exception):
    pass

class PriceChangedException(Exception):
    pass

class InternalTransactionException(Exception):
    pass
