import re


def test2(text):
    findFunction = re.compile('(^[\w]*)\(')
    findParens = re.compile('^[\w]*(\([^()]*\))')
    findParams = re.compile('[^\s(),]+')

    func = findFunction.findall(text)

    params = []
    parens = findParens.findall(text)
    for paren in parens:
        _params = findParams.findall(paren)
        params.extend(_params)


    if func and parens:
        print(func)
        print(parens)
        print(params)


def test(com):
    opCode = ''
    operand = ''
    params = []

    lines = com.split('\n')
    for i, l in enumerate(lines):
        if i == 0:
            words = l.split(' ')
            for j, w in enumerate(words):
                if j == 0:
                    opCode = w
                if j == 1:
                    operand = w
        if i == 1:
            words = l.split('][')
            for w in words:
                # if '[' in w and w[0] == '[':
                params.append(w[:])

    print(i, j, opCode, operand, params)


c1 = 'show configs'
c2 = 'set config\n[configPools][pool2][sym1][300000]'
c3 = 'setConfig(hi, myy, 34)'
c4 = 'showConfigs()'
# test(c2)
test2(c4)
