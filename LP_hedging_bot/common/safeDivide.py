FLOAT_INF = float('inf')


def safeDivide(n1, n2):
    # error case가 적으면 try except가 효율적
    # 많으면 if가 효율적
    try:
        return n1 / n2
    except ZeroDivisionError:
        return FLOAT_INF
