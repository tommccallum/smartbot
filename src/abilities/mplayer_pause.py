from ability import Ability
from skills.mplayer import MPlayer


class MplayerPause(Ability):
    """
    Used to indicate we want to start a new mplayer process
    """

    def __init__(self, on_success=None, on_failure=None):
        super().__init__(on_success, on_failure)
        self.user_context = None

    def perform(self):
        mplayer = None
        if "mplayer" in self.user_context.running:
            print("[INFO] attempting to pause mplayer")
            mplayer = self.user_context.running["mplayer"]
            mplayer.pause_or_play()
            return  mplayer.state == MPlayer.STATE_PAUSED
        return False
