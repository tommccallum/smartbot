from bluetooth_speaker_handler import BluetoothSpeakerHandler
from fifo import read_fifo_nonblocking
from keyboard_thread import KeyboardListener
from states.state import State
from event import Event, EventEnum, EVENT_KEY_UP, EVENT_KEY_RIGHT, EVENT_KEY_LEFT, EVENT_KEY_Q, EVENT_BUTTON_PLAY, \
    EVENT_BUTTON_NEXT, EVENT_BUTTON_PREV
import logging
import threading
import queue
import os
import time
SPEAKER_LOCK_FILE="/tmp/smartbot_connected.lock"

def is_bluetooth_speaker_connected():
    return os.path.isfile(SPEAKER_LOCK_FILE)

class UserContext(BluetoothSpeakerHandler):
    """Main interface to client"""

    """Reference to the current state"""

    def __init__(self, state_objects: list) -> None:
        self._state = None
        self._state_objects = state_objects
        self._current_state_index = -1
        self._state_increment = 1
        self.running = {}
        self.personality = None
        self._listeners = []
        self.interrupted = False
        self.interrupted_state = []
        self.bluetooth_event_fifo = None
        self.ignore_messages = False
        self.queue = queue.Queue()
        self.thread_id = threading.get_ident()
        self.keyboard_thread = None
        logging.debug("Context setup in thread {}".format(self.thread_id))

    def transition_to_named_state(self, name):
        found = -1
        for index, s in enumerate(self._state_objects):
            if s.title.lower() == name.lower():
                found = index
        if found < 0:
            return
        self.transition_to(self._state_objects[found])

    def _notify(self, event):
        """notify listeners of event"""
        event.source = self
        for listener in self._listeners:
            listener.notify(event)

    def start(self):
        """Call this to start the various states that have been enabled"""
        self.check_connected()
        if self.keyboard_thread is None:
            self.keyboard_thread = KeyboardListener()
            self.keyboard_thread.add_listener(self)
            self.keyboard_thread.start()
        self._current_state_index = 0
        self.transition_to(self._state_objects[self._current_state_index])

    def stop(self):
        quit_ev = Event(EventEnum.QUIT)
        if self.keyboard_thread:
            self.keyboard_thread.stop()
        self.add_event(quit_ev)
        # the above will send to the current state but not the rest
        # so we also loop through to ensure everything shutsdown cleaning
        for s in self._state_objects:
            if s != self._state:
                s.notify(quit_ev)
        if self.personality.config.alarm:
            self.personality.config.alarm.stop()

    def transition_to_first(self):
        """Transition to the first state"""
        self._current_state_index = 0
        self.transition_to(self._state_objects[self._current_state_index])

    def transition_to_next(self):
        """
        transition to next, HOWEVER if the user has say pressed the mode button multiple times
        we may skip modes. this is handled by manipulating the self._state_increment variable
        :return:
        """
        self._current_state_index += self._state_increment
        self._current_state_index = self._current_state_index % len(self._state_objects)
        self._state_increment = 1
        self.transition_to(self._state_objects[self._current_state_index])

    def transition_to(self, state: State):
        ## Checking thread to see if when we fire an alarm we
        ## are in a different thread as we need to know what to
        ## do when we change state and we don't want to be fiddling around
        ## with threads
        logging.debug("Thread {}, should be {}".format(threading.get_ident(), self.thread_id))
        self._remove_current_state()
        self._setup_state(state)
        self._state.run()

    def _remove_current_state(self):
        if self._state is not None:
            self._listeners.remove(self._state)
            self._state.on_exit()
            self._state = None

    def _setup_state(self, state):
        self._state = state
        self._state._context = self
        if self._state not in self._listeners:
            self._listeners.append(self._state)

    def is_interrupted(self):
        return len(self.interrupted_state) > 0

    def do_interrupt(self, ev):
        """Triggered when context is interrupted"""
        if self._state is None:
            # we are probably not even started yet, so ignore
            # any interrupts until we are in a valid state
            return
        logging.debug("interrupting current state")
        self.interrupted_state.append( {'state': self._state} )
        if ev is None:
            ev = Event(Event.INTERRUPT)
        self._notify(ev)
        if ev.target_state:
            logging.debug("transitioning to new target state")
            self.transition_to(ev.target_state)


    def do_continue(self):
        """Triggered when context is required to continue after interruption"""
        logging.debug("continuing current state")
        if self.is_interrupted():
            previous_state = self.interrupted_state.pop()
            self.transition_to(previous_state["state"])


    def on_previous_track_down(self):
        self._state.on_previous_track_down()

    def on_previous_track_up(self):
        self._state.on_previous_track_up()

    def on_next_track_down(self):
        self._state.on_next_track_down()

    def on_next_track_up(self):
        self._state.on_next_track_up()

    def on_play_down(self):
        self._state.on_play_down()

    def on_play_up(self):
        self._state.on_play_up()

    def add_event(self, event):
        logging.debug("adding event to queue {}".format(event))
        self.queue.put(event)

    def _check_state_is_finished(self):
        if self._state is not None:
            if self._state.is_finished():
                if self.is_interrupted():
                    self.do_continue()

    def _is_mode_event(self, event):
        if event is None: return False
        if event.id == EventEnum.KEY_PRESS:
            if event.data == EVENT_KEY_UP:
                return True
        elif event.id == EventEnum.BUTTON_DOWN:
            if event.data == EVENT_BUTTON_PLAY:
                return True
        return False

    def _handle_messages(self):
        """
        Handle messages
        :return: True, unless we want to quit
        """
        while not self.queue.empty():
            logging.debug("queue not empty")
            event = self.queue.get()
            if self._is_mode_event(event):
                n = 1 # start from one as its the default for _state_increment
                last_event = event # save current event
                event = self.queue.get()
                while self._is_mode_event(event):
                    n += 1
                    # ignore this new event
                    event = self.queue.get()
                if last_event:
                    self._state_increment = n
                    self._process_message(last_event)
            ret = self._process_message(event)
            if ret == False:
                return False
        return True

    def _process_message(self, event):
        if event is None: return True
        logging.debug("pulling event off queue {}".format(event))
        if event.id == EventEnum.INTERRUPT:
            logging.debug("interrupting")
            self.do_interrupt(event)
        elif event.id == EventEnum.BLUETOOTH_EVENT:
            self._handle_bluetooth_detector(event)
        elif event.id == EventEnum.ENTER_OWNER:
            self._notify(event)
        elif event.id == EventEnum.EXIT_OWNER:
            self._notify(event)
        elif event.id == EventEnum.KEY_PRESS:
            logging.debug("keyboard event detected")
            if event.data == EVENT_KEY_UP:
                self._state.on_play_down()
            if event.data == EVENT_KEY_RIGHT:
                self._state.on_next_track_down()
            if event.data == EVENT_KEY_LEFT:
                self._state.on_previous_track_down()
            if event.data == EVENT_KEY_Q:
                self.stop()
        elif event.id == EventEnum.BUTTON_DOWN:
            logging.debug("device event detected")
            if event.data == EVENT_BUTTON_PLAY:
                self._state.on_play_down()
            if event.data == EVENT_BUTTON_NEXT:
                self._state.on_next_track_down()
            if event.data == EVENT_BUTTON_PREV:
                self._state.on_previous_track_down()

        elif event.id == EventEnum.QUIT:
            ## shut everything down
            self._notify(event)
            return False
        else:
            logging.debug("dropped event {}".format(event))
        return True


    def owner_entered(self, who: str, when: float) -> None:
        ev = Event(EventEnum.ENTER_OWNER)
        ev.data = { "when": when, "who": who }
        self.add_event(ev)

    def owner_exited(self, who: str, when: float) -> None:
        ev = Event(EventEnum.EXIT_OWNER)
        ev.data = {"when": when, "who": who}
        self.add_event(ev)

    def _handle_bluetooth_detector(self, event):
        if self.bluetooth_event_fifo is None:
            logging.debug("bluetooth event fifo is not specified")
            return
        if len(event.data) == 0:
            logging.debug("empty event data")
            return
        logging.debug("bluetooth event found '{}'".format(event))
        try:
            (when, why, owner) = event.data.split(",")
            logging.debug("bluetooth event :: when: {} why: {} who:{}".format(when, why, owner))
            if why.upper() == "ENTER":
                self.owner_entered(owner, when)
            elif why.upper() == "EXIT":
                self.owner_exited(owner, when)
            else:
                logging.debug("unhandled message from bluetooth detector {}".format(event.data))
        except:
            logging.debug("invalid bluetooth event: {}".format(event.data))

    def on_keypress(self, event):
        """this will be coming in to a separate thread!"""
        self.add_event(event)

    def check_connected(self):
        if not is_bluetooth_speaker_connected():
            ## pause everything
            logging.debug("detected speaker is not connected")
            logging.debug("pausing current state")
            ev = Event(EventEnum.DEVICE_LOST)
            self._notify(ev)
            logging.debug("blocking thread until speaker is reconnected, checking every second")
            while not is_bluetooth_speaker_connected():
                logging.debug("checking...")
                time.sleep(1)
            logging.debug("speaker has been reconnected, continuing")
            ev = Event(EventEnum.DEVICE_RECONNECTED)
            self._notify(ev)


    def update(self):
        """
        Should be called in an infinite loop
        :return:
        """
        if self.ignore_messages:
            """
            If this is true we are in a sensitive area and we don't want to be interrupted
            """
            return True
        self.check_connected()
        if self.keyboard_thread is None:
            self.keyboard_thread = KeyboardListener()
            self.keyboard_thread.add_listener(self)
            self.keyboard_thread.start()
        #logging.debug("context update")
        self._check_state_is_finished()
        #logging.debug("context update 3")
        return self._handle_messages()
        #logging.debug("context update 4")