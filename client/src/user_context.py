from actions import inline_action
from activities.activity import Activity
from bluetooth_speaker_handler import BluetoothSpeakerHandler
from capabilities import Capabilities
from fifo import read_fifo_nonblocking, make_fifo
from keyboard_thread import KeyboardListener
from message_handler import TransitionHandler, SilentModeHandler, IdentityHandler, AlarmHandler, BluetoothHandler, \
    NetworkHandler, KeyboardHandler, SpeakerInputHandler, QuitHandler, ReloadHandler
from skills.audio_player import AudioPlayer
from activities.silence_state import SilenceState
from activities.sleep_state import SleepState
from event import Event, EventEnum, EVENT_KEY_UP, EVENT_KEY_RIGHT, EVENT_KEY_LEFT, EVENT_KEY_Q, EVENT_BUTTON_PLAY, \
    EVENT_BUTTON_NEXT, EVENT_BUTTON_PREV
import logging
import threading
import queue
import os
import time

from skills.mplayer_process import MPlayerProcess

SPEAKER_LOCK_FILE="/tmp/smartbot_connected.lock"
LESCANNER_FIFO="lescanner.fifo"

def is_bluetooth_speaker_connected():
    return os.path.isfile(SPEAKER_LOCK_FILE)

class UserContext:
    """Main interface to client"""

    """Reference to the current state"""

    def __init__(self, app_state, activity_objects: list) -> None:

        self.app_state = app_state
        self._current_activity = None
        self._activity_objects = activity_objects
        self._current_activity_index = -1
        self._activity_increment = 1
        self.interrupted = False                                            # True when activity has been interrupted by an Alarm
        self.interrupted_state = []                                         # stack of interrupted states, pop off as each finishes

        self.ignore_messages = False                                        # flag for main loop to stop handling messages
        self.queue = queue.Queue()                                          # queue of events, thread-safe
        self._listeners = []                                                # listeners to the event being dispatched from this class
        self._event_handlers = []                                           # handlers for the events being generated from without

        self.thread_id = threading.get_ident()
        self.keyboard_thread = None                                         # thread for checking for keyboard input
        self.event_device_agent = None                                      # thread for checking for bluetooth speaker events

        self.bluetooth_event_fifo = None
        self.network_detected = False
        self.internet_detected = False

        self.main_loop_sleep = 0.25                                         # sleep in seconds
        self.alarm = None                                                   # set when read new configuration
        self.mplayer_process_object = None                                  # sole audio player interface shared amongst activities
        self.mplayer_owner = None                                           # current object owning the mplayer
        self.capabilities = None

    def config(self):
        return self.app_state.settings

    def personality(self):
        return self.app_state.personality

    def voice(self):
        return self.app_state.voice_library

    def mplayer_is_owner(self, owner):
        """Check if the given owner matches the current owner of the mplayer resource"""
        return self.mplayer_owner == owner

    def mplayer_capture(self, owner):
        """If the mplayer resource is available then owner captures it"""
        if owner is None:
            raise ValueError("owner cannot be None")
        if self.mplayer_owner is not None:
            raise ValueError("thief trying to capture mplayer without owner disconnecting first.")
        logging.debug("Capturing mplayer {}".format(owner.__hash__))
        self.mplayer_owner = owner

    def mplayer_release(self, owner):
        """If the mplayer resource is captured then owner releases it"""
        if self.mplayer != owner:
            raise ValueError("thief trying to release mplayer without owner disconnecting first.")
        logging.debug("Releasing mplayer {}".format(self.mplayer_owner.__hash__))
        self.mplayer_owner = None

    def mplayer_process(self, owner):
        if self.mplayer_owner != owner:
            raise ValueError("thief trying to use mplayer without owner disconnecting first.")
        if self.mplayer_process_object is None:
            mplayer_config_path = self.app_state.settings.find("mplayer.json")
            if mplayer_config_path is None:
                raise ValueError("mplayer configuration file path not defined")
            self.mplayer_process_object = MPlayerProcess(mplayer_config_path, self.app_state.settings.find("fifos"))

        return self.mplayer_process_object

    def start(self):
        """Call this to start the various states that have been enabled"""
        logging.info("Starting application")

        self.capabilities = Capabilities()
        logging.debug(self.capabilities)

        # load all event handlers
        self._event_handlers.append(TransitionHandler())
        self._event_handlers.append(SilentModeHandler())
        if self.capabilities.expect_identity():
            self._event_handlers.append(IdentityHandler())
            self._event_handlers.append(BluetoothHandler())
        self._event_handlers.append(AlarmHandler())
        if self.capabilities.expect_network():
            self._event_handlers.append(NetworkHandler())
        if self.capabilities.expect_keyboard():
            self._event_handlers.append(KeyboardHandler())
        if self.capabilities.expect_bluetooth_speaker():
            self._event_handlers.append(SpeakerInputHandler())
        self._event_handlers.append(QuitHandler())
        self._event_handlers.append(ReloadHandler())

        if self.capabilities.expect_network():
            self._check_network_connected()
        if self.capabilities.expect_bluetooth_speaker():
            self._check_bluetooth_connected()
        if self.capabilities.expect_keyboard():
            self._start_keyboard_monitor()
        if self.capabilities.expect_identity():
            self._start_bluetooth_events()

        self._current_activity_index = 0
        # we should check if we are already in a sleep state
        # in which case we should do that transition first
        self._check_for_sleep_mode()
        self.update()

        ev = Event(EventEnum.TRANSITION_TO_FIRST)
        self.add_event(ev)

    def stop(self):
        logging.info("Stopping application")
        if self.alarm is not None:
            self.alarm.stop()
        if self.event_device_agent is not None:
            self.event_device_agent.stop()
        quit_ev = Event(EventEnum.QUIT)
        if self.keyboard_thread:
            self.keyboard_thread.stop()
        self.add_event(quit_ev)
        # the above will send to the current state but not the rest
        # so we also loop through to ensure everything shutsdown cleaning
        for s in self._activity_objects:
            if s != self._current_activity:
                s.notify(quit_ev)

    def is_no_activity_set(self):
        return self._current_activity is None

    def is_activity_active(self):
        return self._current_activity.is_active()

    def notify(self, event):
        """
        notify listeners of event, normally the current state is the main listener
        """
        event.source = self
        for listener in self._listeners:
            listener.notify(event)

    def _main_loop(self):
        """
        Main application loop listening for events
        :return:
        """
        while True:
            if not self.update():
                break
            time.sleep(self.main_loop_sleep)

    def _start_bluetooth_events(self):
        """
        Setup us listening for other bluetooth devices that may indicate people coming and going
        :return:
        """
        fifo_full_path = make_fifo(self.config(), LESCANNER_FIFO)
        self.bluetooth_event_fifo = fifo_full_path

    def _remove_current_activity(self):
        if self._current_activity is not None:
            self._listeners.remove(self._current_activity)
            self._current_activity.on_exit()
            self._current_activity = None

    def _setup_activity(self, activity):
        self._current_activity = activity
        self._current_activity._context = self
        if self._current_activity not in self._listeners:
            self._listeners.append(self._current_activity)

    def is_interrupted(self):
        return len(self.interrupted_state) > 0

    def add_event(self, event):
        logging.debug("adding event to queue ID {}".format(event.id))
        self.queue.put(event)

    def _check_current_activity_is_finished(self):
        if self._current_activity is not None:
            if self._current_activity.is_finished():
                if self.is_interrupted():
                    ev = Event(EventEnum.ALARM_CONTINUE)
                    self.add_event(ev)

    def _process_messages_waiting_in_queue(self):
        """
        Handle messages
        :return: True, unless we want to quit
        """
        while not self.queue.empty():
            logging.debug("queue not empty")
            event = self.queue.get()
            if event.is_mode_event():
                logging.debug("is play down event")
                if not self.queue.empty():
                    logging.debug("more than 1 event found in queue")
                    n = 1  # start from one as its the default for _state_increment
                    last_event = event  # save current event
                    event = self.queue.get()
                    while event.is_mode_event():
                        n += 1
                        # ignore this new event
                        if not self.queue.empty():
                            event = self.queue.get()
                        else:
                            event = None
                            break
                    logging.debug("is play down event {}".format(n))
                    if last_event:
                        logging.debug("doing last play event")
                        self._activity_increment = n
                        self._dispatch_message(last_event)
            logging.debug("doing event")
            ret = self._dispatch_message(event)
            if ret == False:
                return False
        return True

    def _dispatch_message(self, event):
        if event is None: return True
        logging.debug("pulling event off queue with ID {}".format(event.id))

        handle_count = 0
        for handler in self._event_handlers:
            if handler.expects(event.id):
                ok_to_continue = handler.execute(self, event)
                handle_count += 1
                if not ok_to_continue:
                    return False
        if handle_count == 0:
            logging.debug("dropping event ID {}".format(event.id))
        return True

    # def _process_message(self, event):
    #     if event is None: return True
    #     logging.debug("pulling event off queue with ID {}".format(event.id))
    #
    #     override_sleep_signal = False
    #     if hasattr(event, "override_ignorable_events"):
    #         if event.override_ignorable_events:
    #             override_sleep_signal = True
    #
    #     if not self.is_asleep() or override_sleep_signal:
    #         if event.id == EventEnum.TRANSITION_TO_FIRST:
    #             self.transition_to_first()
    #         elif event.id == EventEnum.TRANSITION_TO_NEXT:
    #             self.transition_to_next()
    #         elif event.id == EventEnum.TRANSITION_TO_NAMED:
    #             self.transition_to_named_state(event.data)
    #         elif event.id == EventEnum.ENTER_OWNER:
    #             self._notify(event)
    #         elif event.id == EventEnum.EXIT_OWNER:
    #             self._notify(event)
    #
    #     if event.id == EventEnum.ALARM_INTERRUPT:
    #         logging.debug("interrupting")
    #         self.do_alarm_interrupt(event)
    #     elif event.id == EventEnum.BLUETOOTH_EVENT:
    #         self._handle_bluetooth_detector(event)
    #     elif event.id == EventEnum.NETWORK_FOUND or \
    #         event.id == EventEnum.NETWORK_LOST or \
    #         event.id == EventEnum.INTERNET_FOUND or \
    #         event.id == EventEnum.INTERNET_LOST:
    #         self._notify(event)
    #     elif event.id == EventEnum.KEY_PRESS:
    #         logging.debug("keyboard event detected")
    #         if event.data == EVENT_KEY_Q:
    #             self.stop()
    #         elif event.data == EVENT_KEY_UP:
    #             self._current_activity.on_play_down()
    #         elif event.data == EVENT_KEY_RIGHT:
    #             self._current_activity.on_next_track_down()
    #         elif event.data == EVENT_KEY_LEFT:
    #             self._current_activity.on_previous_track_down()
    #     elif event.id == EventEnum.BUTTON_DOWN:
    #         logging.debug("device event detected")
    #         if event.data == EVENT_BUTTON_PLAY:
    #             self._current_activity.on_play_down()
    #         if event.data == EVENT_BUTTON_NEXT:
    #             self._current_activity.on_next_track_down()
    #         if event.data == EVENT_BUTTON_PREV:
    #             self._current_activity.on_previous_track_down()
    #     elif event.id == EventEnum.QUIT:
    #         ## shut everything down
    #         self._notify(event)
    #         return False
    #     elif event.id == EventEnum.ENTER_SLEEP_NOW:
    #         self.go_to_sleep(event)
    #     elif event.id == EventEnum.ENTER_SLEEP_IF_ABLE:
    #         self.go_to_sleep(event)
    #     elif event.id == EventEnum.EXIT_SLEEP:
    #         self._notify(event)
    #     elif event.id == EventEnum.RELOAD_CONFIG:
    #         self.handle_reload_config()
    #     else:
    #         logging.debug("dropping event ID {}".format(event.id))
    #     return True
    #

    def on_keypress(self, event):
        """
        this will be coming in to a separate thread (see keyboard_thread.py!
        """
        self.add_event(event)

    def _start_keyboard_monitor(self):
        if not self.capabilities.expect_keyboard():
            return
        if self.keyboard_thread is None:
            self.keyboard_thread = KeyboardListener()
            self.keyboard_thread.add_listener(self)
            self.keyboard_thread.start()

    def _check_bluetooth_connected(self):
        if not self.config.bluetooth_speaker_capability:
            return
        if not is_bluetooth_speaker_connected():
            ## pause everything
            logging.debug("detected speaker is not connected")
            logging.debug("pausing current state")
            ev = Event(EventEnum.DEVICE_LOST)
            self.notify(ev)
            logging.debug("blocking thread until speaker is reconnected, checking every second")
            while not is_bluetooth_speaker_connected():
                logging.debug("checking...")
                time.sleep(1)
            logging.debug("speaker has been reconnected, continuing")
            ev = Event(EventEnum.DEVICE_RECONNECTED)
            self.notify(ev)

    def _check_network_connected(self):
        """
        Checks network and raises events to take action
        We check the INTERNET first and then the local NETWORK.  This in on purpose.
        """
        network_path="/tmp/smartbot_network.lock"
        internet_path = "/tmp/smartbot_internet.lock"

        if self.config.internet_monitor_capability:
            if os.path.isfile(internet_path):
                if self.internet_detected == False:
                    self.internet_detected = True
                    ev = Event(EventEnum.INTERNET_FOUND)
                    self.add_event(ev)
            else:
                if self.internet_detected == True:
                    self.internet_detected = False
                    ev = Event(EventEnum.INTERNET_LOST)
                    self.add_event(ev)

        if self.config.network_monitor_capability:
            if os.path.isfile(network_path):
                if self.network_detected == False:
                    self.network_detected = True
                    ev = Event(EventEnum.NETWORK_FOUND)
                    self.add_event(ev)
            else:
                if self.network_detected == True:
                    self.network_detected = False
                    ev = Event(EventEnum.NETWORK_LOST)
                    self.add_event(ev)

    def _check_for_sleep_mode(self):
        if self._current_activity.is_sleep_state():
            if self.sleep_mode.is_ready_to_wake_up():
                wake_up_event = self.sleep_mode.create_wake_up_event()
                self.add_event(wake_up_event)
                self.sleep_mode.setup_sleep_timings()
        else:
            # this code will keep pinging out sleep requests UNTIL we actually go to sleep
            sleep_event = self.sleep_mode.is_ready_to_sleep()
            if sleep_event:
                sleep_event.target_state = SleepState(self.app_state, {})
                self.add_event(sleep_event)

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
        self._check_bluetooth_connected()
        self._check_network_connected()
        self._check_for_sleep_mode()
        self._check_current_activity_is_finished()
        return self._process_messages_waiting_in_queue()

    def is_asleep(self):
        if self._current_activity:
            return self._current_activity.is_sleep_state()
        return False
