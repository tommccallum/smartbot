from bluetooth_speaker_handler import BluetoothSpeakerHandler


class DebugContext(BluetoothSpeakerHandler):
    """Simply output the function called by the device"""
    def on_previous_track_down(self):
        print("on_previous_track_down")
    def on_previous_track_up(self):
        print("on_previous_track_up")
    def on_next_track_down(self):
        print("on_next_track_down")
    def on_next_track_up(self):
        print("on_next_track_up")
    def on_play_down(self):
        print("on_play_down")
    def on_play_up(self):
        print("on_play_up")