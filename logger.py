from datetime import datetime
from typing import List

class levels:
    WARNING = "WARNING"
    INFO = "INFO"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    HEADER = "HEADER"

    def get_hierarchy(selected: 'levels') -> List['levels']:
        tmp = [levels.DEBUG, levels.INFO, levels.WARNING, levels.ERROR, levels.HEADER]
        return tmp[tmp.index(selected):]
        

class logger_class:
    __slots__ = "log_file", "allowed", "log_to_console"

    def __init__(self, log_file: str, clear: bool = False, level: levels = levels.INFO, log_to_console: bool = False) -> None:
        self.log_file = log_file
        self.allowed = levels.get_hierarchy(level)
        self.log_to_console = log_to_console
        if clear:
            with open(log_file, "w"): pass

    def _log(self, level: levels, data: str, counter) -> None:
        if level not in self.allowed: return
        log_msg = f"{counter} [{level}]: {data}\n"
        with open(self.log_file, "a") as f:
            f.write(log_msg)
        if self.log_to_console:
            print(log_msg, end="")
    
    def log(self, level: levels, data: str, counter: str = str(datetime.now())) -> None:
        if level == levels.INFO:
            self.info(data, counter)
        elif level == levels.WARNING:
            self.warning(data, counter)
        elif level == levels.ERROR:
            self.error(data, counter)
        elif level == levels.HEADER:
            self.header(data, counter)
        else:
            self.debug(data, counter)

    def header(self, data: str, counter: str = str(datetime.now())):
        decor = list("="*40)
        decor.insert(int(20-len(data) / 2), data)
        final_decor = decor[0:int(20-len(data) / 2) + 1]
        final_decor.extend(decor[int((20-len(data) / 2) + len(data)):])
        self._log(levels.HEADER, "".join(final_decor), counter)

    def debug(self, data: str, counter: str = str(datetime.now())):
        self._log(levels.DEBUG, data, counter)

    def warning(self, data: str, counter: str = str(datetime.now())) -> None:
        self._log(levels.WARNING, data, counter)

    def info(self, data: str, counter: str = str(datetime.now())) -> None:
        self._log(levels.INFO, data, counter)

    def error(self, data: str, counter: str = str(datetime.now())):
        self._log(levels.ERROR, data, counter)
