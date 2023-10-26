import glob
import logging
import os

import mne

from src.config import CONFIG

_log = logging.Logger(__name__)

def loadData(path: [None | str] = None) -> mne.io.Raw:
    _path = path
    supportedFileTypes = {
        "gdf" : {}
    }
    
    if _path is not None:
        data_format = os.path.splitext(_path)[1].strip(".")
    elif CONFIG.hasKey("raw_data_path"):
        # if config explicitly specifies a data file
        _path = CONFIG.data
        data_format = os.path.splitext(_path)[1].strip(".")
    else:
        # Get the latest data recorded in the data dir of the format specified
        # in the config, if it exists
        data_dir = CONFIG.data_dir
        data_format = CONFIG.data_format
        _log.debug("No data specified, checking data dir: %s", data_dir)
        files = glob.glob(data_dir + "\\**\\*." + data_format, recursive=True)
        if len(files) == 0:
            raise RuntimeError(
                f"No data (filetype = {data_format}) found in data dir: " +
                f"{data_dir}"
            )
        _path = max(files, key=os.path.getctime)
        
    if not data_format in supportedFileTypes:
        raise ValueError(
            f"Unsupported file type `{data_format}`. Supported file types: " +
            f"{supportedFileTypes.keys()}"
        )
        
    _log.debug("Loading data from file: %s", _path)
    raw = mne.io.read_raw(_path, **supportedFileTypes[data_format])
    
    return raw
    
    
    
    