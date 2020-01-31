from ability import Ability
from skills.mplayer import MPlayer


class MplayerStart(Ability):
    """
    Used to indicate we want to start a new mplayer process
    """

    def __init__(self, track, on_success=None, on_failure=None):
        super().__init__(on_success, on_failure)
        self.track = track
        self.user_context = None

    def perform(self):
        if not self.track:
            print("[WARNING] no track was found in object")
        else:
            mplayer = None
            if "mplayer" in self.user_context.running:
                mplayer = self.user_context.running["mplayer"]
            else:
                mplayer = MPlayer()
                self.user_context.running["mplayer"] = mplayer
            mplayer.start(self.track)
            return True
        return False
