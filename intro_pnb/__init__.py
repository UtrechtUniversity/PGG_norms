from otree.api import *


doc = """
Introduction and elicitation of personal normative beliefs
for the linear and stepwise public goods games.

The order of the two elicitation tasks corresponds to the order
in which the participant will subsequently play the games.
"""

from settings import (
    number_of_players as np,
    players_per_group as ppp,
    endowment as e,
    num_rounds as nr,
    efficiency_factor as ef,
    threshold as t,
    reward as r,
    contribution_time as ct,
    observation_time as ot,
)

class C(BaseConstants):
    NAME_IN_URL = "intro_pnb"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    title = "Multiplayer decision-making game"
    endowment = e
    efficiency_factor = ef
    threshold = t
    reward = r


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    pnb_linear = models.CurrencyField(
        min=0,
        max=C.endowment,
        initial=None,
        verbose_name=(
            "According to you, what is the appropriate amount "
            "that each member should contribute to the group account?"
        ),
        widget=widgets.RadioSelect,
        choices=[
            i for i in range(C.endowment + 1)
        ],
    )

    pnb_stepwise = models.CurrencyField(
        min=0,
        max=C.endowment,
        initial=None,
        verbose_name=(
            "According to you, what is the appropriate amount "
            "that each member should contribute to the group account?"
        ),
        widget=widgets.RadioSelect,
        choices=[
            i for i in range(C.endowment + 1)
        ],
    )

    prolific_id = models.StringField(default="")


def linear_is_first(player):
    return (
        player.session.config["public_goods_first"]
        == "linear"
    )


def stepwise_is_first(player):
    return (
        player.session.config["public_goods_first"]
        == "stepwise"
    )


def store_pnb_values(player):
    """
    Store both PNB values so that they remain available
    in subsequent apps.
    """

    player.participant.vars["pnb_linear"] = int(
        player.pnb_linear
    )

    player.participant.vars["pnb_stepwise"] = int(
        player.pnb_stepwise
    )

    player.participant.vars[
        "ready_for_selection"
    ] = True


class IntroductionPage(Page):

    @staticmethod
    def before_next_page(
        player,
        timeout_happened,
    ):
        player.prolific_id = (
            player.participant.label or ""
        )

    @staticmethod
    def vars_for_template(player):
        return dict(
            endowment=C.endowment,
            efficiency_factor=C.efficiency_factor,
            threshold=C.threshold,
            reward=C.reward,
            players_per_group=ppp,
            other_players=ppp-1,
            rounds=nr,
            total_rounds=2*nr,
            first_game=player.session.config[
                "public_goods_first"
            ],
        )


class PNBLinearFirst(Page):
    """
    Shown first only when the linear game is played first.
    """

    form_model = "player"
    form_fields = ["pnb_linear"]

    template_name = "intro_pnb/PNBLinear.html"

    @staticmethod
    def is_displayed(player):
        return linear_is_first(player)

    @staticmethod
    def vars_for_template(player):
        return dict(
            endowment=C.endowment,
            efficiency_factor=C.efficiency_factor,
            players_per_group=ppp,
            game_type="linear",
            elicitation_number=1,
        )

    @staticmethod
    def error_message(player, values):
        if values.get("pnb_linear") is None:
            return (
                "Please indicate what you think is "
                "the appropriate contribution."
            )


class PNBStepwiseFirst(Page):
    """
    Shown first only when the stepwise game is played first.
    """

    form_model = "player"
    form_fields = ["pnb_stepwise"]

    template_name = "intro_pnb/PNBStepwise.html"

    @staticmethod
    def is_displayed(player):
        return stepwise_is_first(player)

    @staticmethod
    def vars_for_template(player):
        return dict(
            endowment=C.endowment,
            threshold=C.threshold,
            reward=int(C.reward),
            players_per_group=ppp,
            game_type="stepwise",
            elicitation_number=1,
        )

    @staticmethod
    def error_message(player, values):
        if values.get("pnb_stepwise") is None:
            return (
                "Please indicate what you think is "
                "the appropriate contribution."
            )


class PNBLinearSecond(Page):
    """
    Shown second only when the stepwise game is played first.
    """

    form_model = "player"
    form_fields = ["pnb_linear"]

    template_name = "intro_pnb/PNBLinear.html"

    @staticmethod
    def is_displayed(player):
        return stepwise_is_first(player)

    @staticmethod
    def vars_for_template(player):
        return dict(
            endowment=C.endowment,
            efficiency_factor=C.efficiency_factor,
            players_per_group=ppp,
            game_type="linear",
            elicitation_number=2,
        )

    @staticmethod
    def error_message(player, values):
        if values.get("pnb_linear") is None:
            return (
                "Please indicate what you think is "
                "the appropriate contribution."
            )

    @staticmethod
    def before_next_page(
        player,
        timeout_happened,
    ):
        store_pnb_values(player)


class PNBStepwiseSecond(Page):
    """
    Shown second only when the linear game is played first.
    """

    form_model = "player"
    form_fields = ["pnb_stepwise"]

    template_name = "intro_pnb/PNBStepwise.html"

    @staticmethod
    def is_displayed(player):
        return linear_is_first(player)

    @staticmethod
    def vars_for_template(player):
        return dict(
            endowment=C.endowment,
            threshold=C.threshold,
            reward=int(C.reward),
            players_per_group=ppp,
            game_type="stepwise",
            elicitation_number=2,
        )

    @staticmethod
    def error_message(player, values):
        if values.get("pnb_stepwise") is None:
            return (
                "Please indicate what you think is "
                "the appropriate contribution."
            )

    @staticmethod
    def before_next_page(
        player,
        timeout_happened,
    ):
        store_pnb_values(player)


page_sequence = [
     IntroductionPage,

    # Exactly one of these two pages is displayed.
    PNBLinearFirst,
    PNBStepwiseFirst,

    # Exactly one of these two pages is displayed.
    PNBLinearSecond,
    PNBStepwiseSecond,
]