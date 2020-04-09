from abc import ABC, abstractmethod


class Ability(ABC):
    """
        An ability is a wrapper for a skill that can be added to OUTPUT for responding to requests.
        Essentially a bit like a future in that it contains some action to do in the future when
        called.
    """

    def __init__(self, on_success=None, on_failure=None):
        self.on_success = on_success
        self.on_failure = on_failure

    @abstractmethod
    def perform(self):
        """Do the action that has been requested"""
        pass

    def run(self):
        if self.perform():
            if self.on_success:
                self.on_success.run()
        else:
            if self.on_failure:
                self.on_failure.run()