from collections import defaultdict

dd = defaultdict(lambda: None)

print(dd['a'])

dd['a'] = 'a'

print(dd['a'])

s = 'BTCUSDT'
f = 'USDT'

print(s[-len(f):])
if (s[-len(f):] == f):
    ticker = s.split(f)[0]
    market = f
    print(ticker, market)

infiniteDict = lambda: defaultdict(infiniteDict)

infdict = infiniteDict()

infdict['a']['b']['c']['d'] = 1
print(infdict['a']['b']['c']['d'])
print(infdict['d'])

oderbook = defaultdict(lambda: defaultdict(lambda: [[0, 0]] * 5))

print(oderbook['btc']['ask'])

bid = [[1, 1], [2, 2], [3, 3], [4, 4]]

for i,[p,q] in enumerate(bid):
    print(i,p,q)

sym = 'BTCUSDT'
print({'symbol': sym})