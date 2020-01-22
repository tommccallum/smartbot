import os

from config_io import DEFAULT_CONFIG_LOCATION


def make_fifo(filename):
    path = os.path.join(DEFAULT_CONFIG_LOCATION, "fifos")
    if not os.path.isdir(path):
        print("[INFO] Creating directory: " + path)
        os.makedirs(path)
    fifo = os.path.join(path, filename)
    if not os.path.isfile(fifo):
        os.mkfifo(fifo)
    return fifo