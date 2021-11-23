from datetime import datetime
from typing import List
from enum import Enum

class LEVEL(Enum):
    WARNING = "WARNING"
    INFO = "INFO"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    HEADER = "HEADER"

    def get_hierarchy(selected: 'LEVEL') -> List['LEVEL']:
        tmp = [LEVEL.DEBUG, LEVEL.INFO, LEVEL.WARNING, LEVEL.ERROR, LEVEL.HEADER]
        return tmp[tmp.index(selected):]
        
class COLOR(Enum):
    INFO = "\033[92m"
    ERROR = "\033[91m"
    WARNING = "\033[93m"
    HEADER = "\033[94m"
    END = "\033[0m"

    def from_level(level: LEVEL) -> "COLOR":
        return getattr(COLOR, level.value)

class logger_class:
    __slots__ = "log_file", "allowed", "log_to_console"

    def __init__(self, log_file: str, clear: bool = False, level: LEVEL = LEVEL.INFO, log_to_console: bool = False) -> None:
        self.log_file = log_file
        self.allowed = LEVEL.get_hierarchy(level)
        self.log_to_console = log_to_console
        if clear:
            with open(log_file, "w"): pass

    def _log(self, level: LEVEL, data: str, counter) -> None:
        if level not in self.allowed: return
        log_msg = f"[{counter}] [{level.value}]: {data}"
        with open(self.log_file, "a") as f:
            f.write(log_msg)
            f.write("\n")
        if self.log_to_console:
            print(f"{COLOR.from_level(level).value}{log_msg}{COLOR.END.value}")
    
    def log(self, level: LEVEL, data: str, counter: str = str(datetime.now())) -> None:
        if level == LEVEL.INFO:
            self.info(data, counter)
        elif level == LEVEL.WARNING:
            self.warning(data, counter)
        elif level == LEVEL.ERROR:
            self.error(data, counter)
        elif level == LEVEL.HEADER:
            self.header(data, counter)
        else:
            self.debug(data, counter)

    def header(self, data: str, counter: str = str(datetime.now())):
        decor = list("="*40)
        decor.insert(int(20-len(data) / 2), data)
        final_decor = decor[0:int(20-len(data) / 2) + 1]
        final_decor.extend(decor[int((20-len(data) / 2) + len(data)):])
        self._log(LEVEL.HEADER, "".join(final_decor), counter)

    def debug(self, data: str, counter: str = str(datetime.now())):
        self._log(LEVEL.DEBUG, data, counter)

    def warning(self, data: str, counter: str = str(datetime.now())) -> None:
        self._log(LEVEL.WARNING, data, counter)

    def info(self, data: str, counter: str = str(datetime.now())) -> None:
        self._log(LEVEL.INFO, data, counter)

    def error(self, data: str, counter: str = str(datetime.now())):
        self._log(LEVEL.ERROR, data, counter)
