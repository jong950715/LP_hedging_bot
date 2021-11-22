def test1(n1):
    try:
        n1 = int(n1)
    except ValueError as e:
        try:
            n1 = float(n1)
        except ValueError as e:
            pass

    print(n1, type(n1))

if __name__ == '__main__':
    test1('1.2')
