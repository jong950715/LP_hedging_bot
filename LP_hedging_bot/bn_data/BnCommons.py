from collections import defaultdict
from binance import AsyncClient

# 전역 변수가 되므로 변수명에 신경쓰자.
FIATS = ['USDT', 'BUSD']
SYMBOL_LU = defaultdict(lambda: None)  # [ticker, market]
MIN_FUTURE_ORDER = 5
MaxOderBookDepth = 20

DIFF_TOL_RATE = 1.05
SPREAD_TOL_RATE = 0.01

'''
symbol : FTMUSDT
ticker : FTM
market : USDT
'''


def symbolToTickerMarket(symbol):  # -> ticker, market
    if SYMBOL_LU[symbol] is None:
        SYMBOL_LU[symbol] = _symbolToTickerMarket(symbol)
    return SYMBOL_LU[symbol]


def _symbolToTickerMarket(symbol):
    for m in FIATS:
        if symbol[-len(m):] == m:
            ticker = symbol.split(m)[0]
            return ticker, m
    else:
        raise Exception("EEE 감별되지 않는 심볼  " + symbol)


def getSymbolsFromPools(configPools):
    symbols = set()
    for pool, configs in configPools.items():
        if configs['sym1'] not in FIATS:
            symbols.add(configs['sym1'])
        if configs['sym2'] not in FIATS:
            symbols.add(configs['sym2'])

    return list(symbols)