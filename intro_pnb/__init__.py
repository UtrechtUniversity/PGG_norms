from otree.api import *
import random


doc = """
Introduction and elicitation of personal normative beliefs
for the linear and stepwise public goods games.

The order of the two elicitation tasks corresponds to the order
in which the participant will subsequently play the games.
"""


from settings import (
    players_per_group as ppp,
    efficiency_factor as ef,
    num_rounds as nr,
)


class C(BaseConstants):
    NAME_IN_URL = "intro_pnb"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    title = "Public goods game"

    endowment = 20

    # Linear game
    efficiency_factor = ef

    # Stepwise game
    threshold = 60
    reward = 15


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

    arrived_waitpage = models.BooleanField(
        initial=False
    )


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


def assign_pnb_tiers(
    players,
    pnb_field,
    participant_var,
    tier_var,
):
    """
    Rank participants on the relevant PNB measure and divide
    them into three tiers

    Participants are randomized before sorting so that ties
    are broken randomly.
    """

    players_randomized = list(players)
    random.shuffle(players_randomized)

    players_sorted = sorted(
        players_randomized,
        key=lambda p: getattr(p, pnb_field),
    )

    num_players = len(players_sorted)

    if num_players % 3 != 0:
        raise ValueError(
            f"The number of participants ({num_players}) "
            "must be divisible by 3 to create equally sized "
            "PNB tiers."
        )

    tier_size = num_players // 3

    for position, player in enumerate(
        players_sorted
    ):
        if position < tier_size:
            tier = "low"

        elif position < 2 * tier_size:
            tier = "middle"

        else:
            tier = "high"

        pnb_value = getattr(
            player,
            pnb_field,
        )

        player.participant.vars[
            participant_var
        ] = pnb_value

        player.participant.vars[
            tier_var
        ] = tier

        print(
            f"Player {player.id_in_subsession} | "
            f"{participant_var}: {pnb_value} | "
            f"{tier_var}: {tier}"
        )


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
            rounds=nr,
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
            reward=C.reward,
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
            reward=C.reward,
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


# ============================================================
# WAIT FOR ALL PNB RESPONSES AND ASSIGN TIERS
# ============================================================

class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True

    template_name = "intro_pnb/ResultsWaitPage.html"

    @staticmethod
    def vars_for_template(player):
        if not player.arrived_waitpage:
            player.arrived_waitpage = True

        players = (
            player.subsession.get_players()
        )

        total_arrived = sum(
            bool(p.arrived_waitpage)
            for p in players
        )

        total_needed = len(
            player.session.get_participants()
        )

        if total_needed == 0:
            percent = 0

        else:
            percent = int(
                (
                    total_arrived
                    / total_needed
                )
                * 100
            )

            # The waitpage disappears when everyone arrives,
            # so keep the visible value below 100.
            percent = min(percent, 99)

        return dict(
            percent=percent,
        )

    @staticmethod
    def after_all_players_arrive(subsession):
        players = subsession.get_players()

        print(
            "\n=== ASSIGNING LINEAR PNB TIERS ==="
        )

        assign_pnb_tiers(
            players=players,
            pnb_field="pnb_linear",
            participant_var="pnb_linear",
            tier_var="pnb_tier_linear",
        )

        print(
            "\n=== ASSIGNING STEPWISE PNB TIERS ==="
        )

        assign_pnb_tiers(
            players=players,
            pnb_field="pnb_stepwise",
            participant_var="pnb_stepwise",
            tier_var="pnb_tier_stepwise",
        )

        print(
            "\n=== PNB TIER ASSIGNMENT COMPLETE ===\n"
        )


page_sequence = [
    #IntroductionPage,

    # Exactly one of these two pages is displayed.
    PNBLinearFirst,
    PNBStepwiseFirst,

    # Exactly one of these two pages is displayed.
    PNBLinearSecond,
    PNBStepwiseSecond,

    ResultsWaitPage,
]