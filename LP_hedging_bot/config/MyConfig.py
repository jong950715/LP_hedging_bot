from common.SingleTonAsyncInit import SingleTonAsyncInit
from config.config import convertType, _getConfigFromFile, getConfigFromFileFitType
import configparser
from definitions import getRootDir
import json

CONFIG_KEYS = '{0}/config/config_keys.ini'.format(getRootDir())
CONFIG_POOLS = '{0}/config/config_pools.ini'.format(getRootDir())
CONFIG_TRADING = '{0}/config/config_trading.ini'.format(getRootDir())
CONFIG_LOGGER = '{0}/config/config_logger.ini'.format(getRootDir())
CONFIG_SCHEDULER = '{0}/config/config_scheduler.ini'.format(getRootDir())
CONFIG_FILE_NAMES = {'configKeys': CONFIG_KEYS,
                     'configPools': CONFIG_POOLS,
                     'configTrading': CONFIG_TRADING,
                     'configLogger': CONFIG_LOGGER,
                     'configScheduler': CONFIG_SCHEDULER}


class MyConfig(SingleTonAsyncInit):
    async def _asyncInit(self):
        self.configs = dict()
        self.loadConfigs()

    def loadConfigs(self):
        for configName, fn in CONFIG_FILE_NAMES.items():
            self.configs[configName] = getConfigFromFileFitType(fn)

    def getConfig(self, name):
        return self.configs[name]

    def processCommand(self, func, params):
        if (func.lower() == 'showConfigs'.lower()) or (func.lower() == 'showAllConfig'.lower()):
            return json.dumps(self.configs, sort_keys=False, indent=4)

        if (func.lower() == 'showConfig'.lower()) or (func.lower() == 'getConfig'.lower()):
            con = self.configs
            for param in params:
                con = con[param]
            return json.dumps(con, sort_keys=False, indent=4)

        if func.lower() == 'setConfig'.lower():
            return self.setConfig(params)

        if func.lower() == 'shutDown'.lower():
            raise Exception('shutDown command has been entered.')

    def setConfig(self, params):
        if len(params) != 4:
            return '인자가 4개 이어야 합니다.'
        configName, section, param, value = params
        if self._validateNewValue(configName, section, param, value):
            self.configs[configName][section][param] = convertType(value)
            config = _getConfigFromFile(CONFIG_FILE_NAMES[configName])
            config[section][param] = value
            with open(CONFIG_FILE_NAMES[configName], 'w') as iniFile:
                config.write(iniFile)
            return '[{0}][{1}][{2}]가 {3}로 변경되었습니다.'.format(*params)
        else:
            return 'type을 체크해주세요.'

    def _validateNewValue(self, configName, section, param, value):
        if type(convertType(value)) == type(self.configs[configName][section][param]):
            return True
        else:
            return False
