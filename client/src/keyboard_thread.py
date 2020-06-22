"""
Detect arrow key for speaker keys and raise similar events
"""
import atexit
import logging
import os
import select
import sys
import threading
import time

import sys, select, tty, termios

from event import EventEnum, Event, EVENT_KEY_UP, EVENT_KEY_DOWN, EVENT_KEY_LEFT, EVENT_KEY_RIGHT, EVENT_KEY_Q


class KeyboardListener(threading.Thread):

    def __init__(self, *args, **kwargs):
        global terminal_old_settings
        super(KeyboardListener, self).__init__(*args, **kwargs)
        logging.debug("creation")
        self._continue = threading.Event()  # is used to suspend the thread's identity
        self._continue.set()  # set to True
        self._running = threading.Event()  # to stop the thread's identity
        self._running.set()  # Set Running to True
        self.listeners = []

    def add_listener(self, obj):
        self.listeners.append(obj)

    def notify(self, ev):
        for l in self.listeners:
            l.on_keypress(ev)

    def handle_key(self, key_code):
        # dont' let any events through once we have finished or when paused
        if not self._running.isSet() or not self._continue.isSet():
            return
        ev = Event(EventEnum.KEY_PRESS)
        if key_code == '\x1b[A':
            logging.debug("up")
            ev.data = EVENT_KEY_UP
        elif key_code == '\x1b[B':
            logging.debug("down")
            ev.data = EVENT_KEY_DOWN
        elif key_code == '\x1b[C':
            logging.debug("right")
            ev.data = EVENT_KEY_RIGHT
        elif key_code == '\x1b[D':
            logging.debug("left")
            ev.data = EVENT_KEY_LEFT
        elif key_code == 'q':
            logging.debug("q")
            ev.data = EVENT_KEY_Q
        if ev is not None:
            self.notify(ev)

    def run(self):
        logging.debug("running")
        while self._running.isSet():
            self._continue.wait()  # returns immediately when false, blocking until the internal identity bit is true to return
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                # tty.setraw(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())
                #logging.debug("waiting for 3 bytes")
                key = sys.stdin.read(1) # blocks until reads 3 bytes, which is correct for arrow keys, will detect CTRL+C
                if key == chr(27):
                    key += sys.stdin.read(2)
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                #logging.debug("handling key")
                if key:
                    self.handle_key(key)
                #logging.debug("flushing")
                #sys.stdin.flush()
            except Exception as e:
                logging.debug(e)
            finally:
                #logging.debug("finally clause")
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            time.sleep(0.2)

    def pause(self):
        logging.debug("pause")
        self._continue.clear()  # set to False to allow threads to block

    def resume(self):
        logging.debug("resume")
        self._continue.set()  # set to True to allow thread to stop blocking

    def stop(self):
        logging.debug("stop")
        self._continue.clear()  # Restores a thread from a paused state. How to have paused
        self._running.clear()  # set to False
        self.join(3) # wait for exit
