dd = dict()
dd[10] = [3, ['a', 'b', 'c']]

for period, (cnt, names) in dd.items():
    print(period)
    print(cnt)
    print(names)
    cnt += 1
    names[0] = 'b'

for period, (cnt, names) in dd.items():
    print(period)
    print(cnt)
    print(names)

print('='*20)
for period, v in dd.items():
    cnt = v[0]
    names = v[1]
    print(period)
    print(cnt)
    print(names)
    v[0] += 1

for period, v in dd.items():
    cnt = v[0]
    names = v[1]
    print(period)
    print(cnt)
    print(names)
    v[0] += 1