from otree.api import Bot, Submission

from . import *


def simulated_contribution(player):
    """
    Return a reproducible contribution between 0 and
    the endowment.
    """
    return (
        player.id_in_subsession
        + player.round_number
        - 2
    ) % (Constants.endowment + 1)


class PlayerBot(Bot):

    def play_round(self):
        selected_for_game = (
            self.participant.vars.get(
                "selected_for_game",
                False,
            )
        )

        if selected_for_game is not True:
            return

        if self.player.round_number == 1:
            yield IntroductionPage

        yield Submission(
            Contribution,
            dict(
                public_investment=simulated_contribution(
                    self.player
                ),
            ),
            check_html=False,
        )

        yield ObservationPage