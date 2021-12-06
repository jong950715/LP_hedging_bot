from collections import defaultdict

orderBook = defaultdict(lambda: defaultdict(lambda: [[None, None]] * 5))
orderBook['update'] = False

if orderBook['update'] is False:
    print('Hi')

print(float(None))