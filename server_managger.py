import subprocess, platform
from logger import logger_class, LEVEL
from typing import List
from time import sleep, perf_counter

class command:
    def __init__(self, string_repr: str) -> None:
        self.string = string_repr
    
    def fill(self, **kwargs) -> "command":
        return command(self.string.format(**kwargs))
    
    def to_cmd(self) -> List[str]:
        return self.string.split(' ')
    
    def __str__(self):
        return self.string

SUCCESS = 0

class managger:
    steam_update_command = command("steamcmd +force_install_dir {path} +login {user_data} +app_update 1690800 validate +quit")
    default_server_path = "~/SatisfactoryDedicatedServer"
    anonime_user_data = "anonymous"
    default_additionals = "-log -unattended"
    windows_run_command = command("{path}/FactoryServer.exe {additionals}")
    linux_run_before = command("chmod +x {path}/Engine/Binaries/Linux/UE4Server-Linux-Shipping")
    linux_run_command = command("{path}/Engine/Binaries/Linux/UE4Server-Linux-Shipping FactoryGame {additionals}")
    def __init__(self, server_path: str = None, steam_username: str = None, steam_password: str = None, logger: logger_class = None, additionals: str = None) -> None:
        self.user_info: str = f"{steam_username} {steam_password}" if steam_username is not None else managger.anonime_user_data
        self.server_path: str = server_path if server_path is not None else managger.default_server_path
        self.server: subprocess.Popen = None
        self.update_server: bool = False
        self.run: bool = True
        self.manual_stop: bool = False
        self.is_running: bool = False
        self.loop_running = False
        self.additionals = additionals if additionals is not None else managger.default_additionals
        self.logger = logger if logger is not None else logger_class("satisfactory_server_managger.lg", LEVEL=LEVEL.INFO)
        self.environment_specific_command: command = managger.windows_run_command if platform.system() == "Windows" else managger.linux_run_command
        logger.info(f"Server managger created with server path: {self.server_path}")

    def _update_server(self) -> bool:
        self.logger.info("Updating server")
        update_command = managger.steam_update_command.fill(user_data=self.user_info, path=self.server_path)
        self.logger.info(f"Update called with following data: {update_command}")
        try:
            subprocess.check_call(update_command.to_cmd())
            return True
        except subprocess.SubprocessError as ex:
            self.logger.error(f"Update exception: {ex}")
            self.logger.warning("Update failed!")
            return False

    def start_server(self, update_before: bool = False) -> bool:
        self.logger.info(f"Start called!")
        if self.is_running:
            self.logger.info("Server start called, while the server is already running!")
            return True
        self.run = True
        if update_before:
            self._update_server()
        self.logger.info("Starting server")
        if platform.system() != "Windows":
            run_before = self.linux_run_before.fill(path=self.server_path)
            subprocess.check_call(run_before.to_cmd())
        start_command = self.environment_specific_command.fill(path=self.server_path, additionals=self.additionals)
        self.server = subprocess.Popen(start_command.to_cmd())
        fail_count = 0
        while self.server.poll() is not None:
            if fail_count == 6:
                self.logger.error("Server start failed!")
                self.server.send_signal()
                return False
            sleep(5)
            fail_count += 1
        self.is_running = True
        self.logger.info("Server started")
        return True
    
    def stop_server(self) -> None:
        if not self.is_running:
            self.logger.info("Stop called while the server is not running!")
            return
        self.logger.info("Stopping server")
        self.manual_stop = True
        self.server.terminate()
        self.logger.info("Waiting for server to stop")
        sleep_count = 1
        sleep(60)
        while self.server.poll() is None:
            self.logger.warning(f"Serve did not terminate after {sleep_count*60} secunds!")
            if sleep_count >= 2: 
                self.logger.info("Trying to kill the server!")
                self.server.kill()
            sleep_count += 1
            sleep(60)
        self.logger.info("Server stopped")
        self.is_running = False
    
    def exit(self) -> None:
        self.logger.info("Exiting server managger...")
        self.run = False
        if self.is_running: self.stop_server()

    def update(self) -> bool:
        self.logger.info("Update called!")
        self.update_server = True
        self.stop_server()
        if self.loop_running:
            return True
        return self._update_server()

    def loop(self) -> None:
        self.logger.info("Loop started")
        self.loop_running = True
        while self.run:
            if not self.is_running:
                self.start_server()
            start_time = perf_counter()
            while self.server.poll() is None:
                if perf_counter() - start_time % 6000 == 0:
                    self.logger.info("Server still running!")
                sleep(1)
            self.is_running = False
            if self.update_server:
                self._update_server()
            if self.manual_stop:
                if not self.update_server:
                    self.logger.info("Server stopped by user!")
                    self.run = False
                self.manual_stop = False
                self.update_server = False
            else:
                self.logger.error("Server unexceptedly stopped!")
        self.loop_running = False
        self.logger.info("Main loop stopped")
