from collections import defaultdict


def defualtValue(*args, **kwargs):
    print('args', args)
    print('kwargs', kwargs)
    return 'default Value'


dd = defaultdict(defualtValue)

print(dd['newKey'])
