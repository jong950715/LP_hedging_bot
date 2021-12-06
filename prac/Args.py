def func1(*args):
    for a in args:
        print(a)

    func2(args)

def func2(*args):
    for a in args:
        print(a)

def funcK(**kwargs):
    for k in kwargs:
        print(k)

    funcK2(k = kwargs)

def funcK2(**kwargs):
    for k in kwargs:
        print(k)

def funcKK(**kwargs):
    if kwargs:
        print("있음")
    else:
        print("없음")
if __name__ == '__main__':
    func1(1,2,3,4,5)
    funcK(a = 1, b=2)
    funcKK()