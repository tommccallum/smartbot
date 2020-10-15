import logging
import sys


def setup_logging():
    """
    Setup default logging structures
    :return:
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    format_string = '[%(asctime)-17s] [%(levelname)-8s] [%(module)-15s] [%(funcName)-10s] %(message)s'
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    root.addHandler(handler)