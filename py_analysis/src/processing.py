import glob
import logging
import os
import re
from typing import Callable

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
        raw: mne.io.Raw, 
        norm_duration: [float|None] = None,
        norm_start: [float|None] = None,
        **kwargs
        ):
    
    # Define default kwargs and overwrite with any specified kwargs
    _kwargs = {
        "start" : 0,
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