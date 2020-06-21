import threading
import logging
import _thread
import time

from event import Event, EventEnum


class BasicThread():
    """
        Basic thread class.
    """
    def __init__(self) -> None:
        super(BasicThread, self).__init__()
        # this is the next state to go to when the user clicks on Next Mode button
        self.running = 0
        self.thread_id = None
        self.thread_pause_flag = threading.Event()
        self.thread_pause_flag.set()
        self.thread_running_flag = threading.Event()
        self.thread_running_flag.set()
        self.thread_delay=0.2

    def do_work_in_thread(self, is_first_run):
        """Override"""
        pass

    def _run(self):
        first_run = True
        while self.thread_running_flag.isSet():
            logging.debug("set waiting to pause to zero")
            self.waiting_to_pause = 0
            logging.debug("check pause flag")
            self.thread_pause_flag.wait()
            logging.debug("do work")
            self.do_work_in_thread(first_run)
            first_run = False
            logging.debug("finished work")
            time.sleep(self.thread_delay) # add a minimal amount to existing timer that should be in child class

    def _start_thread(self):
        logging.debug("starting")
        self.running = 1
        if self.thread_id is None:
            self.thread_id = _thread.start_new_thread(self._run,())
            logging.debug(self.thread_id)
        self.thread_running_flag.set()

    def _pause_thread(self):
        logging.debug("pausing")
        self.running = 0
        self.thread_pause_flag.clear()

    def _resume_thread(self):
        logging.debug("resuming")
        self.running = 1
        self.thread_pause_flag.set()

    def _stop_thread(self):
        logging.debug("stopping")
        self.running = 0
        self.thread_pause_flag.set()
        self.thread_running_flag.clear()
        if self.thread_id is not None:
            threading.join()

    def start(self):
        """ start or resume"""
        if self.thread_id is None:
            self._start_thread()
        else:
            self._resume_thread()

    def stop(self):
        self._stop_thread()

    def pause(self):
        self.waiting_to_pause = 1
        self._pause_thread()
        logging.debug("waiting to complete pause")
        while self.waiting_to_pause == 1:
            time.sleep(self.thread_delay)

    def on_interrupt(self):
        self.waiting_to_pause = 1
        self._pause_thread()
        logging.debug("waiting to complete pause")
        while self.waiting_to_pause == 1:
            time.sleep(self.thread_delay)

    def on_continue(self):
        self._resume_thread()

    def notify(self, event: Event):
        """Purely the receiver of events from context"""
        if event.id == EventEnum.ENTER_OWNER:
            self.on_continue()
        elif event.id == EventEnum.EXIT_OWNER:
            self.on_interrupt()

