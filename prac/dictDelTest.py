from collections import defaultdict

orderBookFt = defaultdict(lambda: defaultdict(lambda: [[0, 0]] * 10))

orderBookFt['sym1']['event'] = 'event1'
orderBookFt['sym2']['event'] = 'event2'
orderBookFt['sym3']['event'] = 'event3'

for k, v in orderBookFt.items():
    print(k, v)
print()

keys = list(orderBookFt.keys())

for k in keys:
    del orderBookFt[k]

for k, v in orderBookFt.items():
    print(k, v)
print()