"""
use evtest to explore /dev/input/event device signals
"""
from evdev import ecodes, InputDevice, categorize, list_devices
from debug_context import DebugContext
from event import Event, EventEnum, EVENT_BUTTON_PREV, EVENT_BUTTON_NEXT, EVENT_BUTTON_PLAY
import asyncio
import threading


class EventDeviceAgent(threading.Thread):
    """
    Agent for handling bluetooth events
    This is done in a separate thread and then
    events are passed to the context add_event which is a queue
    """

    def __init__(self, context, name):
        self.context = context
        self.name = name
        self.loop = None
        self.device = None
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

    def read_event(self):
        if self.device:
            dev = InputDevice(self.device)
            self._async_read_event(dev)
        else:
            raise ValueError("No device name found in configuration.")


    def _async_read_event(self, dev):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._signalcontext(dev))

    def close(self):
        if self.loop:
            self.loop.close()

    async def _signalcontext(self, dev):
        async for ev in dev.async_read_loop():
            # print(repr(ev)+","+ecodes.KEY[ev.code])
            if ev.code != 0:
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
                if ev.code == 200:
                    if ev.value == 1:
                        new_event = Event(EventEnum.BUTTON_DOWN)
                        new_event.data = EVENT_BUTTON_PLAY;
                    else:
                        new_event = Event(EventEnum.BUTTON_DOWN)
                        new_event.data = EVENT_BUTTON_PLAY;
                if new_event is not None:
                    self.context.add_event(new_event)