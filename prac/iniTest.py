import configparser

config = configparser.ConfigParser()
config.read('config_test.ini')
config['pool3']['sym1'] = 'hiru'

with open('config_test.ini', 'w') as conFile:
    config.write(conFile)