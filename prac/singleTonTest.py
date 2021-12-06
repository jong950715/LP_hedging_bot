class SingleTon:
    _ins = None

    def __call__(cls, *args, **kwargs):
        print('call', cls)
        rv = cls.__new__(cls, *args, **kwargs)  # Because __new__ is static!
        if isinstance(rv, cls):
            rv.__init__(*args, **kwargs)
        return rv

    def __new__(cls, *args, **kwargs):
        print('new', cls)
        if cls._ins:
            return cls._ins
        cls._ins = super().__new__(cls)
        return cls._ins


class MyClass(SingleTon):
    def __init__(self, msg):
        print('init', self)
        self.msg = msg

    def myPrint(self):
        print(self.msg)


def example():
    ins1 = MyClass('ins1')
    ins2 = MyClass('ins2')

    ins1.myPrint()
    ins2.myPrint()

    print(ins1)


if __name__ == '__main__':
    example()
