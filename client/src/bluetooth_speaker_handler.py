from abc import abstractmethod, ABC


class BluetoothSpeakerHandler(ABC):
    """
    Abstract class for the bluetooth speaker.
    Methods are not abstract so we only implement the ones we want to
    add functionality to.
    Used by States

    The speaker has 3 buttons so we have 6 possible actions currently.
    """

    def on_previous_track_down(self):
        pass

    def on_previous_track_up(self):
        pass

    def on_next_track_down(self):
        pass

    def on_next_track_up(self):
        pass

    def on_play_down(self):
        pass

    def on_play_up(self):
        pass
