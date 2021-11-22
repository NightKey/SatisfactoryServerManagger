import smdb_api, server_managger
from logger import logger_class, levels
from threading import Thread

logger = logger_class("server_managger_bot.log", level=levels.INFO, log_to_console=True)
managger = server_managger.managger(server_path="/Data/SatisfactoryDedicatedServer", logger=logger)
loop_thread: Thread = None

def start(msg: smdb_api.Message) -> None:
    if not api.is_admin(msg.sender):
        logger.warning("Not admin called the start function!")
        return
    global loop_thread
    started = managger.start_server()
    #TODO: Remove
    server_managger.sleep(30)
    managger.test_stop()
    started = False
    #END TODO
    if started:
        loop_thread = Thread(target=managger.loop)
        loop_thread.name = "Server managger loop"
        loop_thread.start()
    api.send_message("Server started successfully." if started else "Server start failed!", msg.sender)

def stop(msg: smdb_api.Message) -> None:
    if not api.is_admin(msg.sender):
        logger.warning("Not admin called the stop function!")
        return
    managger.exit()
    api.send_message("Server stopped!", msg.sender)

def update(msg: smdb_api.Message) -> None:
    if not api.is_admin(msg.sender):
        logger.warning("Not admin called the update function!")
        return
    updated = managger.update()
    api.send_message("Server restarted successfully!" if updated else "Server restart failed!", msg.sender)

api = smdb_api.API("Satisfactory managger", "a4bdb9b345435631ca6b9c093324ee3a76b8322811fcd82ad04f537946ab6e88")
api.validate()
api.create_function("SFStart", "Starts the satisfactory server. Admin only command.\nUsage: &SFStart\nCategory: HARDWARE", start)
api.create_function("SFUpdate", "Updates the satisfactory server. Admin only command.\nUsage: &SFUpdate\nCategory: HARDWARE", update)
api.create_function("SFStop", "Stops the satisfactory server. Admin only command.\nUsage: &SFStop\nCategory: HARDWARE", stop)
