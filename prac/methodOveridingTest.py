class ClassA:
    def __init__(self, msg):
        self.msg = msg

    def printA(self):
        print(self.msg)

class ClassB:
    def __init__(self, insA : ClassA):
        #self.printB = insA.printA
        self.printB = lambda : insA.printA()

def main():
    insA = ClassA('this method is defined at ClassA.')
    insB = ClassB(insA)
    insB.printB()

if __name__ == "__main__":
    main()
    A = lambda : print("this is made by lambda")
    A()