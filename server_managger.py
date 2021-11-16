import subprocess, platform
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

class signals:
    SUCCESS = 0
    SIGINT = 2
    SIGQUIT = 3
    SIGKILL = 9

class managger:
    steam_update_command = command("steamcmd +login {user_data} +force_install_dir {path} +app_update 1690800 validate +quit")
    default_server_path = "~/SatisfactoryDedicatedServer"
    anonime_user_data = "anonymous"
    windows_run_command = command("cd {path} & FactoryServer.exe -log -unattended")
    linux_run_command = command("cd {path} & ./FactryServer.sh")
    def __init__(self, server_path: str = None, steam_username: str = None, steam_password: str = None, logger: logger_class = None) -> None:
        self.user_info: str = f"{steam_username} {steam_password}" if steam_username is not None else managger.anonime_user_data
        self.server_path: str = server_path if server_path is not None else managger.default_server_path
        self.server: subprocess.Popen
        self.update_server: bool = False
        self.run: bool = True
        self.manual_stop: bool = False
        self.loop_started = False
        self.logger = logger if logger is not None else logger_class("satisfactory_server_managger.lg", levels=levels.INFO)
        self.environment_specific_command: command = managger.windows_run_command if platform.system() == "Windows" else managger.linux_run_command
        logger.info(f"Server managger created with server path: {self.server_path}")

    def _update_server(self) -> None:
        self.logger.header("Updating server")
        update_command = managger.steam_update_command.fill(user_data=self.user_info, path=self.server_path)
        updater = subprocess.Popen(update_command.to_cmd())
        while updater.poll(): sleep(1)
        if updater.returncode != signals.SUCCESS:
            self.logger.warning("Update failed!")

    def start_server(self, update_before: bool = False) -> None:
        self.run = True
        if update_before:
            self._update_server()
        self.logger.header("Starting server")
        start_command = self.environment_specific_command.fill(path=self.server_path)
        self.server = subprocess.Popen(start_command.to_cmd(), shell=True)
    
    def stop_server(self, signal: signals = signals.SIGINT) -> None:
        self.logger.header("Stopping server")
        self.manual_stop = True
        self.server.send_signal(signal)
        counter = 0
        while self.server.poll():
            if counter == 2:
                self.server.send_signal(signals.SIGQUIT)
            if counter == 4:
                self.server.send_signal(signals.SIGKILL)
            sleep(60)
            counter += 1
    
    def exit(self) -> None:
        self.logger.info("Exiting server managger...")
        self.run = False
        if self.server.poll(): self.stop_server(signals.SIGINT)

    def update(self) -> None:
        self.update_server = True
        self.stop_server()
        if self.loop_started:
            return
        self.start_server(True)

    def loop(self) -> None:
        self.loop_started = True
        while self.run:
            self.start_server()
            while self.server.poll():
                sleep(1)
            if self.manual_stop:
                self.manual_stop = False
            else:
                self.logger.error("Server unexceptedly stopped!")
            if self.update_server:
                self._update_server()
                self.update_server = False
        self.logger.info("Main loop stopped")
