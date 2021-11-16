import smdb_api, server_managger
from logger import logger_class, levels
from threading import Thread

logger = logger_class("server_managger_bot.lg", level=levels.INFO, log_to_console=True)
managger = server_managger.managger(server_path="/Data/SatisfactoryDedicatedServer", logger=logger)
loop_thread: Thread = None

def start(msg: smdb_api.Message) -> None:
    if not api.is_admin(msg.sender):
        logger.warning("Not admin called the start function!")
        return
    global loop_thread
    managger.start_server()
    loop_thread = Thread(target=managger.loop)

def stop(msg: smdb_api.Message) -> None:
    if not api.is_admin(msg.sender):
        logger.warning("Not admin called the stop function!")
        return
    managger.exit()

def update(msg: smdb_api.Message) -> None:
    if not api.is_admin(msg.sender):
        logger.warning("Not admin called the update function!")
        return
    managger.update()

api = smdb_api.API("Satisfactory managger", "a4bdb9b345435631ca6b9c093324ee3a76b8322811fcd82ad04f537946ab6e88")
api.validate()
api.create_function("SFStart", "Starts the satisfactory server. Admin only command.\nUsage: &SFStart\nCategory: HARDWARE", start)
api.create_function("SFUpdate", "Updates the satisfactory server. Admin only command.\nUsage: &SFUpdate\nCategory: HARDWARE", update)
api.create_function("SFStop", "Stops the satisfactory server. Admin only command.\nUsage: &SFStop\nCategory: HARDWARE", stop)
