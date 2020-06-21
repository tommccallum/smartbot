"""
use evtest to explore /dev/input/event device signals

was using asyncio but this still seemed to block on async for ev in dev.async_read_loop():
so instead have modified to do blocking calls but in a separate thread.  The events are then
put into the context queue and handled by the main thread.
"""
import logging

from evdev import ecodes, InputDevice, categorize, list_devices

from BasicThread import BasicThread
from event import Event, EventEnum, EVENT_BUTTON_PREV, EVENT_BUTTON_NEXT, EVENT_BUTTON_PLAY
import time

class EventDeviceAgent(BasicThread):
    """
    Agent for handling bluetooth events
    This is done in a separate thread and then
    events are passed to the context add_event which is a queue
    """

    def __init__(self, context, name):
        super().__init__()
        self.context = context
        self.name = name
        self.loop = None
        self.device = None
        self.device_io = None
        self.personality = None
        self.find_device()

    def set_context(self, context):
        self.context = context

    def find_device(self):
        if self.name == None:
            self.device = None
            print("Device name is none, setting device handle to None")
            return
        for path in list_devices():
            input_dev = InputDevice(path)
            if input_dev.name == self.name:
                self.device = path
                print("Found device " + self.name + " at " + self.device)
        if not self.device:
            # fail here, no point saying anything as speaker has not been found
            raise ValueError("Device " + self.name + " is not found")

    def list_devices(self):
        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            print(device.path, device.name, device.phys)

    def open(self):
        if self.device:
            self.device_io = InputDevice(self.device)
        else:
            raise ValueError("No device name found in configuration.")

    def do_work_in_thread(self, is_first_run):
        """Override"""
        if self.device_io is None:
            try:
                logging.debug("attempting to reopen device {}".format(self.device))
                self.open()
                logging.debug("reconnected to virtual device")
            except:
                logging.debug("attempt failed, try again in a bit")
                self.device_io = None
                pass
        if self.device_io is None:
            time.sleep(1)
            return
        try:
            for ev in self.device_io.read_loop():
                if ev.code != 0:
                    logging.debug("device event detected " + repr(ev) + "," + ecodes.KEY[ev.code])
                    new_event = None
                    if ev.code == 165:
                        if ev.value == 1:
                            new_event = Event(EventEnum.BUTTON_DOWN)
                            new_event.data = EVENT_BUTTON_PREV;
                        else:
                            new_event = Event(EventEnum.BUTTON_UP)
                            new_event.data = EVENT_BUTTON_PREV;
                    if ev.code == 163:
                        if ev.value == 1:
                            new_event = Event(EventEnum.BUTTON_DOWN)
                            new_event.data = EVENT_BUTTON_NEXT;
                        else:
                            new_event = Event(EventEnum.BUTTON_UP)
                            new_event.data = EVENT_BUTTON_NEXT;
                    if ev.code == 200: # KEY_PLAYCD
                        if ev.value == 1:
                            new_event = Event(EventEnum.BUTTON_DOWN)
                            new_event.data = EVENT_BUTTON_PLAY;
                        else:
                            new_event = Event(EventEnum.BUTTON_UP)
                            new_event.data = EVENT_BUTTON_PLAY;
                    if ev.code == 201: # KEY_PAUSECD but we use it to change mode as well
                        if ev.value == 1:
                            new_event = Event(EventEnum.BUTTON_DOWN)
                            new_event.data = EVENT_BUTTON_PLAY;
                        else:
                            new_event = Event(EventEnum.BUTTON_UP)
                            new_event.data = EVENT_BUTTON_PLAY;
                    if new_event is not None:
                        logging.debug("adding device event to queue")
                        self.context.add_event(new_event)
        except OSError as err:
            ## mostly likely we lost the device
            logging.debug(err)
            self.device_io = None


    def stop(self):
        if self.loop:
            self.loop.close()
        super().stop()
