import configparser
from definitions import getRootDir

CONFIG_KEYS = '{0}/config/config_keys.ini'.format(getRootDir())
CONFIG_POOLS = '{0}/config/config_pools.ini'.format(getRootDir())
CONFIG_COMMON = '{0}/config/config_common.ini'.format(getRootDir())
CONFIG_FILE_NAMES = {'configKeys': CONFIG_KEYS,
                     'configPools': CONFIG_POOLS,
                     'configCommon': CONFIG_COMMON}
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
    return getConfigFromFileFitType(CONFIG_KEYS)


def _getConfigFromFile(_configFile):
    file = _configFile
    config = configparser.ConfigParser()
    config.read(file, encoding='utf-8')

    return config


def getConfigFromFileFitType(_configFile):
    config = _getConfigFromFile(_configFile)

    res = dict()
    for section in config.sections():
        res[section] = dict()
        for d in config[section]:
            res[section][d] = convertType(config[section][d])

    return res


if __name__ == "__main__":
    # r = getConfigSymbol()
    print('a')
    # config_generator_binance()
    # config_generator_symbol()
    # config_read(CONFIG_SYMBOL)
