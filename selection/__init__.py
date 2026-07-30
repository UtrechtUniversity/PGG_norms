from otree.api import *
import random


doc = """
Selection of the first 72 participants who complete the PNB
elicitation and are present on the waiting page.

Only the selected participants are divided into low, middle,
and high PNB tiers. Participants arriving after the selection
has closed are redirected to the final completion app.
"""

from settings import (
    number_of_players as np,
    players_per_group as ppp,
    endowment as e,
    num_rounds as nr,
    efficiency_factor as ef,
    threshold as t,
    reward as r,
)

class C(BaseConstants):
    NAME_IN_URL = "selection"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    TARGET_PLAYERS = np
    NUMBER_OF_TIERS = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    selected_for_game = models.BooleanField(
        initial=False
    )

    selection_rank = models.IntegerField(
        initial=None
    )

    arrived_waitpage = models.BooleanField(
        initial=False
    )


def creating_session(subsession):
    """
    Initialize the selection variables.
    """

    subsession.session.vars[
        "selection_closed"
    ] = False

    subsession.session.vars[
        "selected_participant_codes"
    ] = []

    for player in subsession.get_players():
        player.selected_for_game = False
        player.selection_rank = None

        player.participant.vars[
            "selected_for_game"
        ] = False


def assign_pnb_tiers(
    players,
    pnb_variable,
    tier_variable,
):
    """
    Rank the selected participants on the relevant PNB
    measure and divide them into three equally sized tiers.

    Participants are randomized before sorting so that ties
    are broken randomly.
    """

    players_randomized = list(players)
    random.shuffle(players_randomized)

    missing_pnb = [
        player.id_in_subsession
        for player in players_randomized
        if pnb_variable
        not in player.participant.vars
    ]

    if missing_pnb:
        raise ValueError(
            f"The following participants have no "
            f"{pnb_variable} value: {missing_pnb}"
        )

    players_sorted = sorted(
        players_randomized,
        key=lambda player: (
            player.participant.vars[
                pnb_variable
            ]
        ),
    )

    number_of_players = len(players_sorted)

    if number_of_players != C.TARGET_PLAYERS:
        raise ValueError(
            f"Expected {C.TARGET_PLAYERS} selected "
            f"participants, but received "
            f"{number_of_players}."
        )

    if (
        number_of_players
        % C.NUMBER_OF_TIERS
        != 0
    ):
        raise ValueError(
            f"The number of selected participants "
            f"({number_of_players}) must be divisible "
            f"by {C.NUMBER_OF_TIERS}."
        )

    tier_size = (
        number_of_players
        // C.NUMBER_OF_TIERS
    )

    for position, player in enumerate(
        players_sorted
    ):
        if position < tier_size:
            tier = "low"

        elif position < 2 * tier_size:
            tier = "middle"

        else:
            tier = "high"

        player.participant.vars[
            tier_variable
        ] = tier

        print(
            f"Player "
            f"{player.id_in_subsession} | "
            f"{pnb_variable}: "
            f"{player.participant.vars[pnb_variable]} | "
            f"{tier_variable}: {tier}"
        )


def group_by_arrival_time_method(
    subsession,
    waiting_players,
):
    """
    Select the first 72 participants who are simultaneously
    present on the waiting page.

    After the selection closes, all other waiting
    participants are marked as not selected and released.
    """

    session = subsession.session

    selection_closed = session.vars.get(
        "selection_closed",
        False,
    )

    # Once the first 72 have been selected, release any
    # remaining or newly arriving participants.
    if selection_closed:

        for player in waiting_players:
            player.selected_for_game = False

            player.participant.vars[
                "selected_for_game"
            ] = False

        print(
            "\n=== RELEASING NON-SELECTED PARTICIPANTS ==="
        )

        print(
            [
                player.id_in_subsession
                for player in waiting_players
            ]
        )

        return waiting_players

    # Keep waiting until 72 participants are present.
    if len(waiting_players) < C.TARGET_PLAYERS:
        return None

    selected_players = waiting_players[
        :C.TARGET_PLAYERS
    ]

    not_ready = [
        player.id_in_subsession
        for player in selected_players
        if not player.participant.vars.get(
            "ready_for_selection",
            False,
        )
    ]

    if not_ready:
        raise ValueError(
            "The following participants reached the "
            "selection app without completing the PNB "
            f"elicitation: {not_ready}"
        )

    for rank, player in enumerate(
        selected_players,
        start=1,
    ):
        player.selected_for_game = True
        player.selection_rank = rank

        player.participant.vars[
            "selected_for_game"
        ] = True

        player.participant.vars[
            "selection_rank"
        ] = rank

    session.vars[
        "selection_closed"
    ] = True

    session.vars[
        "selected_participant_codes"
    ] = [
        player.participant.code
        for player in selected_players
    ]

    print(
        f"\n=== FIRST {C.TARGET_PLAYERS} "
        "PARTICIPANTS SELECTED ==="
    )

    for player in selected_players:
        print(
            f"Rank {player.selection_rank} | "
            f"player "
            f"{player.id_in_subsession} | "
            f"participant code: "
            f"{player.participant.code}"
        )

    return selected_players


class SelectionWaitPage(WaitPage):
    """
    Wait until 72 participants are simultaneously present.

    The progress bar shows the proportion of all session
    participants who have reached this wait page.
    """

    group_by_arrival_time = True

    template_name = (
        "selection/SelectionWaitPage.html"
    )

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

            # Keep the visible value below 100.
            percent = min(percent, 99)

        return dict(
            percent=percent,
        )

    @staticmethod
    def after_all_players_arrive(group):
        players = group.get_players()

        selected_players = [
            player
            for player in players
            if player.selected_for_game
        ]

        # Groups formed after selection has closed contain
        # only non-selected participants.
        if not selected_players:
            return

        if len(selected_players) != C.TARGET_PLAYERS:
            raise ValueError(
                f"The selected group contains "
                f"{len(selected_players)} participants "
                f"instead of {C.TARGET_PLAYERS}."
            )

        print(
            "\n=== ASSIGNING LINEAR PNB TIERS ==="
        )

        assign_pnb_tiers(
            players=selected_players,
            pnb_variable="pnb_linear",
            tier_variable="pnb_tier_linear",
        )

        print(
            "\n=== ASSIGNING STEPWISE PNB TIERS ==="
        )

        assign_pnb_tiers(
            players=selected_players,
            pnb_variable="pnb_stepwise",
            tier_variable="pnb_tier_stepwise",
        )

        print(
            "\n=== PNB TIER ASSIGNMENT COMPLETE ===\n"
        )

class CapacityReached(Page):
    """
    Shown only to participants who arrive after the first
    72 participants have been selected.
    """

    template_name = (
        "selection/CapacityReached.html"
    )

    @staticmethod
    def is_displayed(player):
        return not player.selected_for_game

    @staticmethod
    def app_after_this_page(
        player,
        upcoming_apps,
    ):
        """
        Skip the public-goods-game apps and redirect the
        participant to the final app in the app sequence.

        The final app should therefore be the app containing
        the Prolific completion/payment page.
        """

        if upcoming_apps:
            return upcoming_apps[-1]


page_sequence = [
    SelectionWaitPage,
    CapacityReached,
]