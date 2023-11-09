import glob
import logging
import os
from typing import Any

import yaml

_log = logging.Logger(__name__)

class _Config:
    
    def __init__(self):
        
        # Get the path to the project root directory by searching for the
        # "closest" parent directory that contains a .gitignore file
        root = os.path.dirname(os.path.abspath(__file__))
        target = ".gitignore"
        while len(glob.glob(target, root_dir=root)) == 0:
            # Check if the system root has been reached
            if len(os.path.basename(root)) == 0:
                raise Exception(
                    "Could not find project root directory on path "
                    + os.path.abspath(__file__)
                )
            else:
                root = os.path.dirname(root)
        self.__root = root
        
        # Specify the paths to config files to check in reverse order of
        # priority
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
    
    def __str__(self):
        c = self.__getConfig()
        return str(c)
    
    def hasKey(self, key):
        return key in self.__getConfig()
    
    def snapshot(self) -> dict[str, Any]:
        return self.__getConfig()


CONFIG = _Config()