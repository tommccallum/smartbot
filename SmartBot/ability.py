from abc import ABC, abstractmethod


class Ability(ABC):
    """
        An ability is a wrapper for a skill that can be added to OUTPUT for responding to requests.
        Essentially a bit like a future in that it contains some action to do in the future when
        called.
    """

    @abstractmethod
    def perform(self):
        """Do the action that has been requested"""
        pass