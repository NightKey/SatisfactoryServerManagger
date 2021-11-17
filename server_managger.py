import enum
import subprocess, platform
from enum import Enum
from logger import logger_class, levels
from typing import List
from time import sleep

class command:
    def __init__(self, string_repr: str) -> None:
        self.string = string_repr
    
    def fill(self, **kwargs) -> "command":
        return command(self.string.format(**kwargs))
    
    def to_cmd(self) -> List[str]:
        return self.string.split(' ')
    
    def __str__(self):
        return self.string

class signals(Enum):
    SUCCESS = 0
    SIGINT = 2
    SIGQUIT = 3
    SIGKILL = 9

class managger:
    steam_update_command = command("steamcmd +login {user_data} +force_install_dir {path} +app_update 1690800 validate +quit")
    default_server_path = "~/SatisfactoryDedicatedServer"
    anonime_user_data = "anonymous"
    default_additionals = "-log -unattended"
    windows_run_command = command("{path}/FactoryServer.exe {additionals}")
    linux_run_command = command("{path}/FactoryServer.sh {additionals}")
    def __init__(self, server_path: str = None, steam_username: str = None, steam_password: str = None, logger: logger_class = None, additionals: str = None) -> None:
        self.user_info: str = f"{steam_username} {steam_password}" if steam_username is not None else managger.anonime_user_data
        self.server_path: str = server_path if server_path is not None else managger.default_server_path
        self.server: subprocess.Popen = None
        self.update_server: bool = False
        self.run: bool = True
        self.manual_stop: bool = False
        self.is_running: bool = False
        self.loop_started = False
        self.additionals = additionals if additionals is not None else managger.default_additionals
        self.logger = logger if logger is not None else logger_class("satisfactory_server_managger.lg", levels=levels.INFO)
        self.environment_specific_command: command = managger.windows_run_command if platform.system() == "Windows" else managger.linux_run_command
        logger.info(f"Server managger created with server path: {self.server_path}")

    def _update_server(self) -> None:
        self.logger.info("Updating server")
        update_command = managger.steam_update_command.fill(user_data=self.user_info, path=self.server_path)
        self.logger.info(f"Update called with following data: {update_command}")
        try:
            subprocess.check_call(update_command.to_cmd())
        except subprocess.SubprocessError:
            self.logger.warning("Update failed!")

    def start_server(self, update_before: bool = False) -> bool:
        if self.is_running:
            return
        self.run = True
        if update_before:
            self._update_server()
        self.logger.info("Starting server")
        start_command = self.environment_specific_command.fill(path=self.server_path, additionals=self.additionals)
        self.server = subprocess.Popen(str(start_command), shell=True)
        fail_count = 0
        while not self.server.poll():
            if fail_count == 5:
                return False
            sleep(15)
            fail_count += 1
        self.is_running = True
        self.logger.info(f"Start called with following data: {start_command}")
        return True
    
    def stop_server(self, signal: signals = signals.SIGINT) -> None:
        if not self.is_running:
            return
        self.logger.info("Stopping server")
        self.manual_stop = True
        self.server.send_signal(signal.value)
        self.logger.info(f"Sending signal: {signal.name}")
        counter = 0
        while self.server.poll():
            if counter == 2:
                self.server.send_signal(signals.SIGQUIT.value)
                self.logger.warning(f"Sending signal: {signals.SIGQUIT.name}")
            if counter == 4:
                self.server.send_signal(signals.SIGKILL.value)
                self.logger.warning(f"Sending signal: {signals.SIGKILL.name}")
            sleep(60)
            counter += 1
        self.logger.info("Server stopped")
        self.is_running = False
    
    def exit(self) -> None:
        self.logger.info("Exiting server managger...")
        self.run = False
        if self.is_running: self.stop_server(signals.SIGINT)

    def update(self) -> bool:
        self.update_server = True
        self.stop_server()
        if self.loop_started:
            return True
        return self.start_server(True)

    def loop(self) -> None:
        self.loop_started = True
        while self.run:
            self.start_server()
            while self.server.poll():
                print("..")
                sleep(1)
            if self.manual_stop:
                self.manual_stop = False
            else:
                self.logger.error("Server unexceptedly stopped!")
            if self.update_server:
                self._update_server()
                self.update_server = False
        self.logger.info("Main loop stopped")
