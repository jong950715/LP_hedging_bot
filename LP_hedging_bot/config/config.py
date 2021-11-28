import configparser
from definitions import getRootDir

CONFIG_KEYS = '{0}/config/config_keys.ini'.format(getRootDir())
CONFIG_POOLS = '{0}/config/config_pools.ini'.format(getRootDir())
CONFIG_TRADING = '{0}/config/config_trading.ini'.format(getRootDir())
CONFIG_LOGGER = '{0}/config/config_logger.ini'.format(getRootDir())
CONFIG_SCHEDULER = '{0}/config/config_scheduler.ini'.format(getRootDir())
CONFIG_FILE_NAME = {'configKeys': CONFIG_KEYS,
                    'configPools': CONFIG_POOLS,
                    'configTrading': CONFIG_TRADING,
                    'configLogger': CONFIG_LOGGER,
                    'configScheduler': CONFIG_SCHEDULER}
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

    res['telegram']['chat_id'] = int(res['telegram']['chat_id'])

    return res


def getConfigPools():
    return getConfigFromFileFitType(CONFIG_POOLS)


def getConfigTrading():
    return getConfigFromFileFitType(CONFIG_TRADING)


def getConfigLogger():
    return getConfigFromFileFitType(CONFIG_LOGGER)


def getConfigScheduler():
    return getConfigFromFileFitType(CONFIG_SCHEDULER)


def getConfigFromFile(_configFile):
    file = _configFile
    config = configparser.ConfigParser()
    config.read(file, encoding='utf-8')

    return config


def getConfigFromFileFitType(_configFile):
    config = getConfigFromFile(_configFile)

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
