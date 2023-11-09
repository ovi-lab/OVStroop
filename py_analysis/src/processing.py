import errno
import glob
import logging
import os
import re
from typing import Any, Callable

import matplotlib as mpl
import mne

from src.config import CONFIG

_log = logging.Logger(__name__)

def loadData(
        path: [None | str] = None, 
        checkSubdirs: bool = False,
        **kwargs
        ) -> mne.io.Raw:
    
    # TODO: add logging
    
    # Use values from Config as defined at (approx) loadData call time -
    # prevents issues arising from Config values changes during execution
    _CONFIG_SS = CONFIG.snapshot()
    
    supportedFileTypes = {
        "gdf" : {}
    }
    
    # Determine the path to the raw data file to load, or the folder to search
    # for a data file
    if path is not None:
        # Use the file or folder passed to loadData
        _path = path
    elif _CONFIG_SS.raw_data_path is not None:
        # Use the path to the data raw data file or folder specified in config
        _path = _CONFIG_SS.raw_data_path
    elif _CONFIG_SS.session_name is not None:
        # Find and use the session folder in the data dir
        data_dir = os.path.join(_CONFIG_SS.root, _CONFIG_SS.data_dir)
        targetPath = data_dir + "/**/" + _CONFIG_SS.session_name
        matchingPaths = glob.glob(target, recursive=True)
        if len(matchingPaths) > 1:
            raise RuntimeError(
                "Found multiple directories with session_name " +
                f"'{_CONFIG_SS.session_name}' in data_dir '{data_dir}': " +
                f"{matchingPaths}"
            )
        elif len(matchingPaths) == 0:
            raise RuntimeError(
                "Found no directories with session_name " +
                f"'{_CONFIG_SS.session_name}' in data_dir '{data_dir}': "
            )
        else:
            _path = matchingPaths[0]
    else:
        # Use the entire data dir
        _path = os.path.abspath(
            os.path.join(_CONFIG_SS.root, _CONFIG_SS.data_dir)
        )
        
    invalidFileTypeE = lambda fileType: RuntimeError(
        f"Unsupported file type `{fileType}`. Supported file types: " +
        f"{supportedFileTypes.keys()}"
    )
       
    if os.path.isfile(_path):
        # Use _path as the data file and extract its format directly from _path
        dataFormat = os.path.splitext(_path)[1].strip(".")
        if not dataFormat in supportedFileTypes:
            raise invalidFileTypeE(dataFormat)
        dataPath = _path
    elif os.path.isdir(_path):
        # Get the latest data recorded in _path (or subdirectories if
        # specified) of the format specified in the config
        dataFormat = _CONFIG_SS.data_format
        if not dataFormat in supportedFileTypes:
            raise invalidFileTypeE(datadataFormat_format)
        subdirTarget = "/**" if checkSubdirs else ""
        targetPaths = _path + subdirTarget + "/*." + dataFormat
        matchingPaths = glob.glob(targetPaths, recursive=checkSubdirs)
        
        if len(matchingPaths) == 0:
            raise RuntimeError(
                f"No data (filetype = {dataFormat}) found in directory " +
                f"'{data_dir}'" +
                (" or subdirectories" if checkSubdirs else "")
            )
        dataPath = max(matchingPaths, key=os.path.getctime)
    else:
        raise FileNotFoundError(
            errno.ENOENT, 
            "Specified data is not an existing file or directory", 
            _path
        )
        
    _log.debug("Loading data from file: %s", dataPath)
    _kwargs = {}
    _kwargs.update(supportedFileTypes[dataFormat])
    _kwargs.update(kwargs)
    raw = mne.io.read_raw(dataPath, **_kwargs)
    
    return raw
    
def prettyPlot(
        raw: mne.io.Raw, 
        norm_duration: [float|None] = None,
        norm_start: [float|None] = None,
        **kwargs
        ) -> mpl.figure.Figure:
    
    # Define default kwargs and overwrite with any specified kwargs
    _kwargs = {
        "start" : 0,
        "duration" : 20,
        "n_channels" : min(len(raw.ch_names), 20),
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

def prettyPlotEvoked(
        evoked: mne.Evoked, 
        cleanPlot: bool = True,
        ax: mpl.axes.Axes = None,
        colors: dict[str, Any]|str|None = None,
        units: str = "uV",
        title: str|None = None,
        **kwargs
        ) -> (mpl.axes.Axes, dict[str, mpl.lines.Line2D]):
    _fig, _ax = ax.get_figure(), ax if ax is not None else plt.subplots()
    
    chNames = evoked.ch_names
    if len(set(chNames)) != len(chNames):
        raise ValueError("Channel names must be unique")
    
    # Get color for each channel
    if isinstance(colors, dict):
        _colors = colors
    elif colors is None or isinstance(colors, str):
        cmName = colors if isinstance(colors, str) else "viridis" # by default
        cm = mpl.colormaps[cmName].resampled(len(chNames))
        _colors = {k : v for (k, v) in zip(chNames, cm.colors)}
    else:
        raise ValueError(
            f"Invalid type for argument `colors`: {type(colors)}"
        )
    
    # Do not pass color as additional kwarg, it is handled seperately
    kwargs.pop("color", None)
    
    # Plot the data
    lines = {}  
    data = evoked.get_data(units=units)
    for k, chName in enumerate(chNames):
        lines[chName] = _ax.plot(
            evoked.times,
            data[k],
            label=chName,
            color=_colors[chName],
            **kwargs
        )
        
    # Clean up the plot
    if cleanPlot:
        _ax.set_xlabel("Time (s)")
        _ax.set_ylabel(units)
        _ax.set_title(
            "$N_{ave}=" + str(evoked.nave) + "$", 
            loc="right", 
        )
        _ax.set_title(title)
        
    return _ax, lines
    
def getOVStimCodes() -> dict[str, int]:
    ovStimListPath = os.path.join(CONFIG.root, CONFIG.ov_stim_list_path)
    with open(ovStimListPath, "r") as f:
        lines = f.readlines()
        
    ovStimCodes = {}
    for line in lines:
        entries = line.split()
        ovStimCodes[entries[0]] = int(entries[2], base=16)
        
    if not len(ovStimCodes) == len(lines):
        raise RuntimeError(
            "The number of stimulation codes read from the stimulations " +
            "file is not equal to the number of lines in that file."
        )
        
    return ovStimCodes

def getChannelNames() -> list[str]:
    pass

def ovStimNameEventDict(eventDict: dict[str, int]) -> dict[str, int]:
    # event_dict maps "OV stim id" -> "MNE event id". To insead use the names
    # of the OV stims as keys, use the inverse of the bijective mapping
    # returned by getOvStimCodes(), which maps "OV stim name" -> "OV stim id"
    ovStimCodes = getOVStimCodes()
    ovStimCodesRev = {v: k for k, v in ovStimCodes.items()}
    assert len(ovStimCodes) == len(ovStimCodesRev)
    _eventDict = {ovStimCodesRev[int(k)]: v for k, v in eventDict.items()}

    return _eventDict

def groupEventDict(
        eventDict: dict[str, int],
        by: list[Callable[[str], str|None]]|None = None
        ) -> dict[str, int]:
    
    
    if by is not None:
        _by = by
    else:
        # Default eventDict
        # Assume that all keys in eventDict are OV stimulations
        
        def groupVisStimOnset(s: str) -> str|None:
            if re.search(r"(?<=OVTK_StimulationId_Label_)([1-9]){2}", s):
                return "visual_stimulus_onset"
            else:
                return None
    
        def groupVisStimEnd(s: str) -> str|None:
            if re.search(r"(OVTK_StimulationId_VisualStimulationStop)", s):
                return "visual_stimulus_end"
            else:
                return None
    
        def groupAudStimOnset(s: str) -> str|None:
            if re.search(r"(OVTK_StimulationId_Label_D)[1-4]{1}", s):
                return "auditory_stimulus_onset"
            else:
                return None
    
        def groupAudStimEnd(s: str) -> str|None:
            if re.search(r"(OVTK_StimulationId_Label_D0)", s):
                return "auditory_stimulus_end"
            else:
                return None
    
        def groupCongruentOrNoncongruent(s: str) -> str|None:
            match = re.search(r"(?<=OVTK_StimulationId_Label_)([1-9]){2}", s)
    
            if match is None:
                return None
    
            num = match.group()
            if num[0] == '0':
                return None
            elif num[0] == num[1]:
                return "congruent"
            else:
                return "noncongruent"
    
        def groupBlock(s: str) -> str|None:
            match = re.search(r"(?<=OVTK_StimulationId_Segment)(Start|Stop)", s)
    
            if match is None:
                return None
            else:
                return "block_" + match.group(1).lower()
    
        def groupInstruction(s: str) -> str|None:
            if re.search(R"(OVTK_StimulationId_Label_0)[1-5]{1}", s):
                return "instruction"
            else:
                return None
    
        def groupResponse(s: str) -> str|None:
            if re.search(r"(OVTK_StimulationId_Button)\d{1}(_Pressed)", s):
                return "response"
            else:
                return None
    
        def groupBaseline(s: str) -> str|None:
            if re.search(r"OVTK_GDF_Cross_On_Screen", s):
                return "baseline_start"
            else:
                return None
    
        _by = [
            groupCongruentOrNoncongruent, 
            groupVisStimOnset,
            groupVisStimEnd,
            groupAudStimOnset,
            groupAudStimEnd,
            groupBlock,
            groupInstruction,
            groupResponse
        ]
        
    # Note: not the most efficient, improve?
    _eventDict = {}
    for eventLabel, eventID in eventDict.items():
        _eventLabel = eventLabel # Since eventLabel should be a string this should be safe to copy
        for f in _by:
            condition = f(_eventLabel)
            if condition is not None:
                _eventLabel = condition + "/" + _eventLabel
        _eventDict[_eventLabel] = eventID
        
    return _eventDict