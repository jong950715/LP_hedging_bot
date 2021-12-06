from decimal import Decimal

n1 = float('1e-05')
n2 = float('1e-04')

d1 = Decimal('1e-05')
d2 = Decimal('1e-04')

N1 = int(n1 * 100000000)
N2 = int(n2 * 100000000)

print(n1, n2, n2 % n1)
print(d1, d2, d2 % d1)
print(N1, N2, N2 % N1)
