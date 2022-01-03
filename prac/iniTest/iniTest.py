import configparser

d = {'section1': {'a': '1',
                  'b': '2'},
     'section2': {'a': '11',
                  'b': '22'}
     }

_config = configparser.ConfigParser()
for k, v in d.items():
    _config[k] = v
with open('test.ini', 'w') as iniFile:
    _config.write(iniFile)
