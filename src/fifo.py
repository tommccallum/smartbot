import os

#from config_io import DEFAULT_CONFIG_LOCATION, HOME_DIRECTORY
import config_io

def make_fifo(filename):
    path = os.path.join(os.path.join(config_io.HOME_DIRECTORY,config_io.DEFAULT_CONFIG_LOCATION), "fifos")
    if not os.path.isdir(path):
        print("[INFO] Creating directory: " + path)
        os.makedirs(path)
    fifo = os.path.join(path, filename)
    if not os.path.exists(fifo):
        print("[INFO] Making fifo at "+fifo)
        os.mkfifo(fifo)
    return fifo
