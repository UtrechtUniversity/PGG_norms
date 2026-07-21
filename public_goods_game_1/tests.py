from otree.api import Bot, Submission

from . import *


def simulated_contribution(player):
    """
    Generate reproducible, heterogeneous contributions.

    The pattern generates low- and high-contribution rounds,
    so both possible stepwise threshold outcomes are tested.
    """

    regime = player.session.config[
        "public_goods_first"
    ]

    if regime == "linear":
        pnb_key = "pnb_linear"
    else:
        pnb_key = "pnb_stepwise"

    pnb = int(
        player.participant.vars.get(
            pnb_key,
            10,
        )
    )

    phase = (
        player.round_number - 1
    ) % 4

    if phase == 0:
        # Low-contribution round
        contribution = pnb // 3

    elif phase == 1:
        # High-contribution round
        contribution = pnb + 8

    else:
        # Contributions close to the participant's PNB
        adjustment = (
            (
                player.id_in_subsession
                + player.round_number
            )
            % 5
        ) - 2

        contribution = (
            pnb + adjustment
        )

    return max(
        0,
        min(
            Constants.endowment,
            contribution,
        ),
    )


class PlayerBot(Bot):

    def play_round(self):

        if self.player.round_number == 1:
            yield IntroductionPage

        yield Submission(
            Contribution,
            dict(
                public_investment=(
                    simulated_contribution(
                        self.player
                    )
                ),
            ),
            check_html=False,
        )

        yield ObservationPage