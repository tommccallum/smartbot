import logging

import globalvars


class AppContextLock:
    """
    RAII lock for the app context queue
    Prevents the main loop from processing events until the lock is released.
    """
    _waiting_process_counter=0

    def __init__(self):
        logging.debug("Setting app context lock")
        AppContextLock._waiting_process_counter += 1
        if globalvars.app_state.context:
            globalvars.app_state.context.ignore_messages = True

    def __del__(self):
        AppContextLock._waiting_process_counter -= 1
        if AppContextLock._waiting_process_counter == 0:
            logging.debug("Releasing app context lock")
            if globalvars.app_state.context:
                globalvars.app_state.context.ignore_messages = False