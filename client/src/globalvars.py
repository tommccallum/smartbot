import logging
import sys

app_context = None

def setup_logging():
    """
    Setup default logging structures
    :return:
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)-17s] [%(levelname)-8s] [%(module)-15s] [%(funcName)-10s] %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)