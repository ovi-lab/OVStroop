import logging
import os
from typing import Any

import yaml

_log = logging.Logger(__name__)

class _Config:
    
    def __init__(self):
        self.__configPaths = []
        
        # Path to default config file
        path = os.path.join(os.path.dirname(__file__), "config.yaml")
        self.__configPaths.append(path)
        
        # Path to custom config file
        # TODO: implement
        
    def __getConfig(self) -> dict[str: Any]:
        config = {}
        for k, configPath in enumerate(self.__configPaths):
            try:
                f = open(configPath, 'rt')
            except FileNotFoundError as E:
                if k == 0:
                    errmsg = (
                        "Could not read from default config file: " + 
                        f"{configPath}"
                    )
                    raise RuntimeError(errmsg) from E
                else:
                    _log.debug(
                        "Config file not found at following location, " +
                        "continuing execution: %s", configPath
                    )
            else:
                _log.debug("Loading config file: %s", configPath)
                contents = yaml.load(f, Loader=yaml.FullLoader)
                config.update(contents)
            finally:
                f.close()
                
        return config
                
    def __getattr__(self, name):
        return self.__getConfig()[name]
    
    def hasKey(self, key):
        return key in self.__getConfig()


CONFIG = _Config()