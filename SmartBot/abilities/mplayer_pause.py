from ability import Ability
from skills.mplayer import MPlayer


class MplayerPause(Ability):
    """
    Used to indicate we want to start a new mplayer process
    """

    def __init__(self):
        self.user_context = None

    def perform(self):
        mplayer = None
        if "mplayer" in self.user_context.running:
            mplayer = self.user_context.running["mplayer"]
            mplayer.pause_or_play()
