import time


def getFile(fileName):
    Filename = fileName
    mode = 'a'
    encoding = None
    errors = None
    f = open(Filename, mode, encoding=encoding, errors=errors)
    return f


def test1():
    f = getFile('logTest1.log')
    for i in range(10000):
        msg = '\nHi' + str(i)
        f.write(msg)
        f.flush()


def test2():
    f = getFile('logTest2.log')
    for i in range(10000):
        msg = '\nHi' + str(i)
        f.write(msg)


def main():
    start = time.time()
    test1()
    t = time.time() - start
    print(t)

    start = time.time()
    test2()
    t = time.time() - start
    print(t)


if __name__ == '__main__':
    main()
