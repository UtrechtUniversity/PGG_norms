from otree.api import Bot, Submission

from . import *


class PlayerBot(Bot):

    def play_round(self):
        #if self.player.participant.consent is True:
            yield Submission(
                PaymentInfo,
                {},
                check_html=False,
            )