import _thread
import json
import os
import logging
import threading
import time

from actions import blocking_play, inline_action
from config_io import Configuration
from event import Event, EventEnum
from states.state import State


class ContinuousState(State):
    """
        Plays a thread in the background
        NOT TO BE USED DIRECTLY

        Threading example used is
        https://topic.alibabacloud.com/a/python-thread-pause-resume-exit-detail-and-example-_python_1_29_20095165.html
    """
    def __init__(self,
                 configuration: Configuration,
                 personality: "Personality",
                 state_configuration
                 ) -> None:
        super(ContinuousState, self).__init__(configuration, personality, state_configuration)
        # this is the next state to go to when the user clicks on Next Mode button
        self.running = 0
        self.thread_id = None
        self.thread_pause_flag = threading.Event()
        self.thread_pause_flag.set()
        self.thread_running_flag = threading.Event()
        self.thread_running_flag.set()

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
            time.sleep(0.5) # add a minimal amount to existing timer that should be in child class

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


    def on_empty(self):
        if "on_empty" in self.state_config:
            action = self.state_config["on_empty"]
        else:
            action = "There are no tracks available on this playlist."
        inline_action( action )

    def on_enter(self):
        if self.state_config is not None:
            action = self.state_config["on_enter"]
        else:
            action = "Welcome, you are listening to {}".format(self.state_config["title"])
        inline_action(action)
        if self.thread_id is None:
            self._start_thread()
        else:
            self._resume_thread()


    def on_exit(self):
        self.waiting_to_pause = 1
        self._pause_thread()
        logging.debug("waiting to complete pause")
        while self.waiting_to_pause == 1:
            time.sleep(0.2)

    def on_previous_track_down(self):
        """In this mode, the previous button pauses the currently playing song"""
        if self.running:
            self._pause_thread()
            self.personality.voice_library.say("Pausing, press the same button to continue")
        else:
            self._resume_thread()

    def on_play_down(self):
        logging.debug("trying to move on")
        self._pause_thread()
        self.context.transition_to_next()

    def on_interrupt(self):
        self.waiting_to_pause = 1
        self._pause_thread()
        logging.debug("waiting to complete pause")
        while self.waiting_to_pause == 1:
            time.sleep(0.2)

    def on_continue(self):
        self._resume_thread()

    def notify(self, event: Event):
        """Purely the receiver of events from context"""
        if event.id == EventEnum.ENTER_OWNER:
            self.on_continue()
        elif event.id == EventEnum.EXIT_OWNER:
            self.on_interrupt()

