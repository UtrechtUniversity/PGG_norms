from otree.api import Bot

from . import *


class PlayerBot(Bot):

    def play_round(self):
        if not self.player.selected_for_game:
            yield CapacityReached