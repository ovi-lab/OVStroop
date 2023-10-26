import logging
import os
from typing import Any

import yaml

_log = logging.Logger(__name__)

class _Config:
    
    def __init__(self):
        
        # get the path to OVStroop directory
        rootName = "OVStroop"
        root = os.path.abspath(__file__)
        while os.path.basename(root) != rootName:
            root = os.path.dirname(root)
            if not os.path.basename(root):
                raise Exception(
                    f"Could not find target root directory `{rootName}` on path "
                    + os.path.abspath(__file__)
                    )
        self.__root = root
        
        self.__configPaths = []
        
        # Path to default config file
        path = os.path.join(os.path.dirname(__file__), "config.yaml")
        self.__configPaths.append(path)
        
        # Path to custom config file
        path = os.path.join(self.__root, "py_analysis", "config.yaml")
        self.__configPaths.append(path)
        
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
                contents = {} if contents is None else contents
                config.update(contents)
            finally:
                f.close()
                
        config["root"] = self.__root
        return config
                
    def __getattr__(self, name):
        return self.__getConfig()[name]
    
    def hasKey(self, key):
        return key in self.__getConfig()


CONFIG = _Config()