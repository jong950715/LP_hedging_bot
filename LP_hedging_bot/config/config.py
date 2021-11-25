import configparser
from definitions import getRootDir

CONFIG_KEYS = '/config/config_keys.ini'
CONFIG_POOLS = '/config/config_pools.ini'
CONFIG_TRADING = '/config/config_trading.ini'

'''
ini는 대소문자 안가림
'''


def convertType(n):
    try:
        n = int(n)
    except ValueError as e:
        try:
            n = float(n)
        except ValueError as e:
            pass
    return n


def config_read(config_file):
    pass


def getConfigKeys():
    config = getConfigFromFile(CONFIG_KEYS)

    res = dict()
    for section in config.sections():
        res[section] = dict()
        for d in config[section]:
            res[section][d] = config[section][d]

    return res


def getConfigPools():
    config = getConfigFromFile(CONFIG_POOLS)

    res = dict()
    for section in config.sections():
        res[section] = dict()
        for d in config[section]:
            res[section][d] = convertType(config[section][d])

    return res


def getConfigTrading():
    config = getConfigFromFile(CONFIG_TRADING)

    res = dict()
    for section in config.sections():
        res[section] = dict()
        for d in config[section]:
            res[section][d] = convertType(config[section][d])

    return res


def getConfigFromFile(_configFile):
    file = getRootDir() + _configFile
    config = configparser.ConfigParser()
    config.read(file, encoding='utf-8')

    return config


if __name__ == "__main__":
    # r = getConfigSymbol()
    print('a')
    # config_generator_binance()
    # config_generator_symbol()
    # config_read(CONFIG_SYMBOL)
