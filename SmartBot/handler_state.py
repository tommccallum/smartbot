from bluetooth_speaker_handler import BluetoothSpeakerHandler


class HandlerState(BluetoothSpeakerHandler):
    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context) -> None:
        self._context = context

    def on_enter(self):
        """on entering this new state"""
        pass

    def on_exit(self):
        """on transitioning from this state"""
        pass