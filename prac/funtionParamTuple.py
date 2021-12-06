def fun1(str1, str2, str3):
    print(str1, str2, str3)


if __name__ == "__main__":
    tup = ('a', 'b', 'c')
    fun1('a', 'b', 'c')
    fun1(*tup)
    li = [('a', 'b', 'c'), ('a', 'b', 'c')]
    for a, b, c in li:
        print(a)
        print(b)
        print(c)
