from decimal import Decimal

price = Decimal('10.95')
priceStep = Decimal('0.1')


price = priceStep * round(price / priceStep)

print(price)
