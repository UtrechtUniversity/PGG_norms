from otree.api import Bot

from . import *


def simulated_pnb(player, offset=0):
    """Return a reproducible value between 0 and the endowment."""
    return (
        player.id_in_subsession - 1 + offset
    ) % (C.endowment + 1)


class PlayerBot(Bot):

    def play_round(self):
        linear_pnb = simulated_pnb(self.player)
        stepwise_pnb = simulated_pnb(self.player, offset=7)

        first_game = self.player.session.config[
            "public_goods_first"
        ]

        if first_game == "linear":
            yield PNBLinearFirst, dict(
                pnb_linear=linear_pnb,
            )
            yield PNBStepwiseSecond, dict(
                pnb_stepwise=stepwise_pnb,
            )

        elif first_game == "stepwise":
            yield PNBStepwiseFirst, dict(
                pnb_stepwise=stepwise_pnb,
            )
            yield PNBLinearSecond, dict(
                pnb_linear=linear_pnb,
            )

        else:
            raise ValueError(
                "public_goods_first must be "
                "'linear' or 'stepwise'."
            )