import glob
import logging
import os

import mne

from src.config import CONFIG

_log = logging.Logger(__name__)

def loadData(path: [None | str] = None, **kwargs) -> mne.io.Raw:
    _path = path
    supportedFileTypes = {
        "gdf" : {}
    }
    
    if _path is not None:
        data_format = os.path.splitext(_path)[1].strip(".")
    elif CONFIG.hasKey("raw_data_path"):
        # if config explicitly specifies a data file
        _path = CONFIG.raw_data_path
        data_format = os.path.splitext(_path)[1].strip(".")
    else:
        # Get the latest data recorded in the data dir of the format specified
        # in the config, if it exists
        data_dir = os.path.join(CONFIG.root, CONFIG.data_dir)
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
    _kwargs = {}
    _kwargs.update(supportedFileTypes[data_format])
    _kwargs.update(kwargs)
    raw = mne.io.read_raw(_path, **_kwargs)
    
    return raw
    
    
def prettyPlot(
        raw, 
        norm_duration: [float|None] = None,
        norm_start: [float|None] = None,
        **kwargs
        ):
    
    # Define default kwargs and overwrite with any specified kwargs
    _kwargs = {
        "start" : 0,
        "duration" : raw.times[-1],
        "n_channels" : len(raw.ch_names),
        "scalings" : 'auto',
    }
    _kwargs.update(kwargs)
    
    # Overwrite start time and duration if normalised values are specified
    if norm_start is not None:
        _kwargs["start"] = norm_start * raw.times[-1]
    if norm_duration is not None:
        _kwargs["duration"] = norm_duration * raw.times[-1]
    
    # Trim duration to fit inside actual length of signal
    _kwargs["duration"] = min(
        _kwargs["duration"],
        raw.times[-1] - _kwargs["start"]
    )
    
    return raw.plot(**_kwargs)
    
    
    