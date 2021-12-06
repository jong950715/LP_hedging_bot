#Case 1
class A1(object):
    def __init__(self):
        print("A init")

class B1(A1):
    def __init__(self):
        print("B init")
        super(B1, self).__init__()  #ok, I can invoke A's __init__ successfully

#Case 2
class A2(object):
    @classmethod
    def foo(cls):
        print("A foo")

class B2(A2, object):
    @classmethod
    def foo(cls):
        print("B foo")
        super(B2, cls).foo()   #ok, I can invoke A's foo successfully

#Case 3
class A3(object):
    def __new__(cls):
      print("A new")
      return super(A3, cls).__new__(cls)

class B3(A3):
    def __new__(cls):
      print("B new")
      print(B3, cls)
      return super(B3, cls).__new__(cls)  #Oops, error

def main():
    B3()

if __name__ == '__main__':
    main()