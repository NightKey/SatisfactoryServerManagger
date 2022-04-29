import smdb_api, server_managger
from logger import logger_class, LEVEL
from threading import Thread
from time import sleep
from random import randint

logger = logger_class("server_managger_bot.log", level=LEVEL.INFO, log_to_console=True)
managger = server_managger.managger(server_path="/Data/SatisfactoryDedicatedServer", logger=logger)
loop_thread: Thread = None

def start(msg: smdb_api.Message) -> None:
    if not api.is_admin(msg.sender):
        logger.warning("Not admin called the start function!")
        api.send_message("Only admins can use this command!", msg.sender)
        return
    global loop_thread
    started = managger.start_server()
    if started:
        loop_thread = Thread(target=managger.loop)
        loop_thread.name = "Server managger loop"
        loop_thread.start()
    api.send_message("Server started successfully." if started else "Server start failed!", msg.sender)

def stop(msg: smdb_api.Message) -> None:
    if not api.is_admin(msg.sender):
        logger.warning("Not admin called the stop function!")
        api.send_message("Only admins can use this command!", msg.sender)
        return
    managger.exit()
    api.send_message("Server stopped!", msg.sender)

def update(msg: smdb_api.Message) -> None:
    if not api.is_admin(msg.sender):
        logger.warning("Not admin called the update function!")
        api.send_message("Only admins can use this command!", msg.sender)
        return
    updated = managger.update()
    api.send_message(("Server restarted successfully!" if managger.loop_running else "Server updated successfully!") if updated else "Server update failed!", msg.sender)

def restart(msg: smdb_api.Message) -> None:
    if not api.is_admin(msg.sender):
        logger.warning("Not admin called the start function!")
        api.send_message("Only admins can use this command!", msg.sender)
        return
    restart = managger.restart()
    api.send_message("Server restarted successfully!" if restart else "Server update failed!", msg.sender)

def is_running(msg: smdb_api.Message) -> None:
    api.send_message("The server is up and running" if managger.is_running else "The server is stopped", msg.sender)

logger.debug(f"Random id: {randint(0,10)}")

api = smdb_api.API("Satisfactory managger", "a4bdb9b345435631ca6b9c093324ee3a76b8322811fcd82ad04f537946ab6e88")
api.validate()
api.create_function("SFStart", "Starts the satisfactory server. Admin only command.\nUsage: &SFStart\nCategory: HARDWARE", start)
api.create_function("SFUpdate", "Updates the satisfactory server. Admin only command.\nUsage: &SFUpdate\nCategory: HARDWARE", update)
api.create_function("SFStop", "Stops the satisfactory server. Admin only command.\nUsage: &SFStop\nCategory: HARDWARE", stop)
api.create_function("SFRestart", "Restarts the satisfactory server if it's running, othervise starts a new one. Admin only command.\nUsage: &SFRestart\nCategory: HARDWARE", restart)
api.create_function("SFStatus", "Returns the satisfactory server's status.\nUsage: &SFStatus\nCategory: HARDWARE", is_running)
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    logger.info("User terminating the bot!")
    logger.info("Stopping Satisfactory server...")
    managger.stop_server()
    api.close("User interrupt")