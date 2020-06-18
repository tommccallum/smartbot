import os
import logging
import errno
import _thread
import time

from event import Event, EventEnum

BUFFER_SIZE = 1024

def make_fifo(configuration, filename):
    """
    Creates fifo file and returns path to it
    """
    path = configuration.get_fifo_directory()
    if not os.path.isdir(path):
        logging.info("Creating directory: " + path)
        os.makedirs(path)
    fifo = os.path.join(path, filename)
    if not os.path.exists(fifo):
        logging.info("Making fifo at " + fifo)
        os.mkfifo(fifo)
    return fifo

def read_fifo_nonblocking(file_path):
    """read fifo file in a nonblocking style"""
    if not os.path.exists(file_path):
        return
    try:
        io = os.open(file_path, os.O_RDONLY | os.O_NONBLOCK)
        buffer = os.read(io, BUFFER_SIZE)
    except OSError as err:
        if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
            buffer = None
        else:
            raise  # something else has happened -- better reraise
    return buffer


def read_fifo_thread_main(file_path, context):
    io = os.open(file_path, os.O_RDONLY | os.O_NONBLOCK)
    while True:
        try:
            buffer = os.read(io, BUFFER_SIZE)
            if buffer is not None and len(buffer) > 0:
                logging.debug("Received data from fifo")
                ev = Event(EventEnum.BLUETOOTH_EVENT)
                ev.data = buffer.decode("utf-8")
                context.add_event(ev)
        except OSError as err:
            if err.errno != errno.EAGAIN and err.errno != errno.EWOULDBLOCK:
                logging.debug(err)
        finally:
            time.sleep(0.5)


def read_fifo_in_thread(file_path, context):
    """
    Read a fifo in a separate thread, writer will shut
    when we close this file.
    :param file_path:
    :return:
    """
    if not os.path.exists(file_path):
        logging.error("{} not found".format(file_path))
        return
    # @todo add some management of this thread perhaps?
    _thread.start_new_thread(read_fifo_thread_main, (file_path,context,) )