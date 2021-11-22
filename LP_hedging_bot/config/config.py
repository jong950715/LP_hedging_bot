import configparser
import definitions

CONFIG_KEYS = '/config/config_keys.ini'
CONFIG_SYMBOL = '/config/config_symbol.ini'
CONFIG_POOL = '/config/config_pool.ini'

'''
ini는 대소문자 안가림
'''


def config_generator_symbol():
    config = configparser.ConfigParser()

    config['FTMUSDT'] = {}
    config['FTMUSDT']['K'] = str(500 * 500)
    config['FTMUSDT']['price_step'] = str(0.00001)
    config['FTMUSDT']['qty_step'] = str(1)

    # 설정파일 저장
    with open(CONFIG_SYMBOL, 'w', encoding='utf-8') as configfile:
        config.write(configfile)


def convertType(n):
    try:
        n = int(n)
    except ValueError as e:
        try:
            n = float(n)
        except ValueError as e:
            pass
    return n
    print(n, type(n))


def config_read(config_file):
    pass


def getConfigKeys():
    file = getConfigFile(CONFIG_KEYS)
    config = configparser.ConfigParser()
    config.read(file, encoding='utf-8')

    res = dict()

    for section in config.sections():
        res[section] = dict()
        for d in config[section]:
            res[section][d] = config[section][d]

    return res


def getConfigPool():
    file = getConfigFile(CONFIG_POOL)
    config = configparser.ConfigParser()
    config.read(file, encoding='utf-8')

    res = dict()

    for section in config.sections():
        res[section] = dict()
        for d in config[section]:
            res[section][d] = convertType(config[section][d])

    return res


def getConfigFile(_configFile):
    return definitions.getRootDir() + _configFile


if __name__ == "__main__":
    # r = getConfigSymbol()
    print('a')
    # config_generator_binance()
    # config_generator_symbol()
    # config_read(CONFIG_SYMBOL)
