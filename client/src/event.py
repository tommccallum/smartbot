from enum import Enum

EVENT_KEY_UP=0
EVENT_BUTTON_PLAY=0
EVENT_KEY_DOWN=1
## no down button equivalent on speaker
EVENT_KEY_LEFT=2
EVENT_BUTTON_PREV=2
EVENT_KEY_RIGHT=3
EVENT_BUTTON_NEXT=3
EVENT_KEY_Q = 4

class EventEnum(Enum):
    """different events"""
    NO_EVENT = 0
    INTERRUPT = 1
    CONTINUE = 2
    ALARM = 3
    ENTER_OWNER = 4
    EXIT_OWNER = 5
    DEVICE_FOUND = 6
    DEVICE_LOST=7,
    BLUETOOTH_EVENT=8
    KEY_PRESS=10,
    BUTTON_DOWN=11,
    BUTTON_UP=12,
    DEVICE_RECONNECTED=14,
    NETWORK_FOUND=15,
    NETWORK_LOST=16,
    INTERNET_FOUND=17,
    INTERNET_LOST=18,
    QUIT=255


class Event:
    """
    Event object which is used for various interruptions to the current state

    The target_state is the state that you want the context to transition to on interrupt.
    Without this set nothing will happen.
    """

    def __init__(self, id: EventEnum):
        """
        Create an event
        :param id:  the EventEnum
        """
        self.source = None
        self.id = id
        self.data = {}
        self.target_state = None
