from common.SingleTonAsyncInit import SingleTonAsyncInit
from config.config import convertType, _getConfigFromFile, getConfigFromFileFitType, CONFIG_FILE_NAMES
import configparser
from definitions import getRootDir
import json
from bn_data.BnCommons import getSymbolsFromPools, FIATS
import asyncio
from collections import deque


class MyConfig(SingleTonAsyncInit):
    async def _asyncInit(self, pSymbols):
        self.configs = dict()
        self.loadConfigs()
        self.pSymbols = pSymbols
        self.paramsForPools = deque()

    def loadConfigs(self):
        for configName, fn in CONFIG_FILE_NAMES.items():
            self.configs[configName] = getConfigFromFileFitType(fn)

    def getConfig(self, name):
        return self.configs[name]

    async def runScript(self, func, params):
        if (func.lower() == 'showConfigs'.lower()) or (func.lower() == 'showAllConfig'.lower()):
            return json.dumps(self.configs, sort_keys=False, indent=4)

        if (func.lower() == 'showConfig'.lower()) or (func.lower() == 'getConfig'.lower()):
            if len(params) > 4:
                return '인자가 너무 많습니다.'
            con = self.configs
            for param in params:
                con = con[param]
            return json.dumps(con, sort_keys=False, indent=4)

        if func.lower() == 'setConfig'.lower():
            return await self.setConfig(params)

        if func.lower() == 'shutDown'.lower():
            raise Exception('shutDown command has been entered.')

        if func.upper() == 'addPool'.upper():
            return self.addPool(params)

    async def setConfig(self, params):
        if len(params) != 4:
            return '인자가 4개 이어야 합니다.'

        res = self._validateSetConfig(params)
        if res == True:
            await self._setConfig(params)
            return '[{0}][{1}][{2}]가 {3}로 변경되었습니다.'.format(*params)
        else:
            return res

    async def _setConfig(self, params):
        configName, section, param, value = params

        self.configs[configName][section][param] = convertType(value)  # write@memory
        self._saveFileAsMemory(configName)  # write@file

    def _validateSetConfig(self, params):
        configName, section, param, value = params

        if (configName.upper() == 'configPools'.upper()) and ('sym' in param):
            return 'symbol은 변경할 수 없습니다.'

        if configName.upper() == 'configKeys'.upper():
            return 'Key는 변경할 수 없습니다.'

        if type(convertType(value)) == type(self.configs[configName][section][param]):
            return True
        else:
            return 'Type을 확인해주세요.'

    def _saveFileAsMemory(self, configName):
        _config = configparser.ConfigParser()
        for k, v in self.configs[configName].items():
            _config[k] = v
        with open(CONFIG_FILE_NAMES[configName], 'w') as iniFile:
            _config.write(iniFile)

    def validateAddPoolParams(self, params):
        if len(params) != 6:
            return '파라미터 수가 안맞음'

        if params[0] in self.configs['configPools'].keys():
            return 'pool name 중복'

        params[1] = params[1].upper()
        params[2] = params[2].upper()

        return True

    def addPool(self, params):
        res = self.validateAddPoolParams(params)
        if res == True:
            self.paramsForPools.append(params)
            return 'pool이 추가되었습니다.'
        else:
            return res

    def checkPoolUpdate(self):
        if len(self.paramsForPools) == 0:
            return False
        else:
            self._addPool(*self.paramsForPools.popleft())
            return True

    def _addPool(self, section, sym1, sym2, k, sym1_target, sym2_target):

        self._addSymbolInPools(sym1)
        self._addSymbolInPools(sym2)

        self.configs['configPools'][section] = dict()
        self.configs['configPools'][section]['sym1'] = convertType(sym1)
        self.configs['configPools'][section]['sym2'] = convertType(sym2)
        self.configs['configPools'][section]['k'] = convertType(k)
        self.configs['configPools'][section]['sym1_target'] = convertType(sym1_target)
        self.configs['configPools'][section]['sym2_target'] = convertType(sym2_target)
        self._saveFileAsMemory('configPools')

        return 'pool이 추가되었습니다.'

    def _addSymbolInPools(self, sym):
        sym = sym.upper()
        if (sym not in self.pSymbols[0]) and (sym not in FIATS):
            self.pSymbols[0].append(sym)

    async def _beforeConfigPools(self, newSymbols):
        for sym in newSymbols:
            self._addSymbolInPools(sym)
        self.pSymbols[1] = True
        self.pSymbols[2] = True
        #  await asyncio.sleep(5)

    def _afterConfigPools(self):
        self.pSymbols[0] = getSymbolsFromPools(self.getConfig('configPools'))
        self.pSymbols[1] = True
        self.pSymbols[2] = True