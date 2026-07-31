from otree.api import *
import random


doc = """
First public goods game.

Participants are assigned to six-person groups based on their
personal normative beliefs. The game type and group composition
are determined by the session-level treatment conditions.
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
    introduction_time as it,
)

from pgg_functions import (
    set_payoffs as calculate_pgg_payoffs,
    handle_contribution_timeout,
    get_regime,
    get_composition,
    get_tier_variable,
    get_pnb_variable,
    get_injunctive_feedback,
)


class Constants(BaseConstants):
    name_in_url = "public_goods_game_1"

    target_players = np
    players_per_group = ppp
    num_rounds = nr

    num_recent_rounds_to_display = 1

    endowment = e

    # Linear game
    efficiency_factor = ef

    # Stepwise game
    threshold = t
    reward = r


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_group_investment = models.CurrencyField(
        initial=0
    )

    # False: descriptive feedback only
    # True: descriptive + injunctive feedback
    show_feedback = models.BooleanField(
        initial=False
    )

    regime = models.StringField()
    composition = models.StringField()

    def set_payoffs(self):
        calculate_pgg_payoffs(self)


class Player(BasePlayer):
    payoff_from_private = models.CurrencyField()

    payoff_from_public = models.CurrencyField()

    gross_profit = models.CurrencyField(
        initial=0
    )

    public_investment = models.CurrencyField(
        min=0,
        max=Constants.endowment,
        verbose_name=(
            "How much would you like to invest "
            "in the public account?"
        ),
    )

    contribution_timed_out = models.BooleanField(
        initial=False
    )

def creating_session(subsession):
    if subsession.round_number == 1:
        subsession.session.vars[
            "game_1_groups_planned"
        ] = False



def create_homogeneous_groups(
    players,
    tier_variable,
):
    """
    Create homogeneous groups by randomly assigning
    participants within their low, middle, or high PNB tier.
    """

    group_size = Constants.players_per_group

    players_by_tier = {
        "low": [],
        "middle": [],
        "high": [],
    }

    for player in players:
        tier = player.participant.vars.get(
            tier_variable
        )

        if tier not in players_by_tier:
            raise ValueError(
                f"Player {player.id_in_subsession} "
                f"has no valid {tier_variable}."
            )

        players_by_tier[tier].append(
            player
        )

    matrix = []

    for tier in [
        "low",
        "middle",
        "high",
    ]:
        tier_players = players_by_tier[tier]

        if (
            len(tier_players)
            % group_size
            != 0
        ):
            raise ValueError(
                f"The {tier} tier contains "
                f"{len(tier_players)} participants, "
                f"which is not divisible by the "
                f"group size ({group_size})."
            )

        #  randomize participants within this tier.
        random.shuffle(tier_players)

        for start in range(
            0,
            len(tier_players),
            group_size,
        ):
            group_players = tier_players[
                start:start + group_size
            ]

            # Also randomize id_in_group.
            random.shuffle(group_players)

            matrix.append(group_players)

    # Randomize which tier receives which group number.
    random.shuffle(matrix)

    return matrix


def create_heterogeneous_groups(
    players,
    tier_variable,
):
    """
    Create groups with equal numbers of low, middle,
    and high-PNB participants.


    """

    group_size = Constants.players_per_group

    if group_size % 3 != 0:
        raise ValueError(
            f"The group size ({group_size}) must be "
            "divisible by 3 to create heterogeneous groups."
        )

    number_per_tier_per_group = (
        group_size // 3
    )

    players_by_tier = {
        "low": [],
        "middle": [],
        "high": [],
    }

    for player in players:
        tier = player.participant.vars.get(
            tier_variable
        )

        if tier not in players_by_tier:
            raise ValueError(
                f"Player {player.id_in_subsession} "
                f"has no valid {tier_variable}."
            )

        players_by_tier[tier].append(player)

    number_of_players = len(players)

    if number_of_players % group_size != 0:
        raise ValueError(
            f"The number of participants "
            f"({number_of_players}) is not divisible "
            f"by the group size ({group_size})."
        )

    number_of_groups = (
        number_of_players // group_size
    )

    required_per_tier = (
        number_of_groups
        * number_per_tier_per_group
    )

    for tier, tier_players in (
        players_by_tier.items()
    ):
        if len(tier_players) != required_per_tier:
            raise ValueError(
                f"The {tier} tier contains "
                f"{len(tier_players)} participants; "
                f"{required_per_tier} are required."
            )

        random.shuffle(tier_players)

    matrix = []

    for group_number in range(
        number_of_groups
    ):
        start = (
            group_number
            * number_per_tier_per_group
        )

        end = (
            start
            + number_per_tier_per_group
        )

        group_players = (
            players_by_tier["low"][start:end]
            + players_by_tier["middle"][start:end]
            + players_by_tier["high"][start:end]
        )

        random.shuffle(group_players)
        matrix.append(group_players)

    random.shuffle(matrix)

    return matrix


def plan_feedback_conditions(
    matrix,
    composition,
    tier_variable,
):
    """
    Preassign feedback to every planned group.

    For homogeneous groups, randomize feedback separately
    within each PNB tier.

    For heterogeneous groups, randomize feedback across all
    planned groups.
    """

    feedback_by_group = {}

    if composition == "homogeneous":

        groups_by_tier = {
            "low": [],
            "middle": [],
            "high": [],
        }

        for group_number, group_players in enumerate(
            matrix,
            start=1,
        ):
            group_tiers = {
                player.participant.vars.get(
                    tier_variable
                )
                for player in group_players
            }

            if len(group_tiers) != 1:
                raise ValueError(
                    f"Planned homogeneous group "
                    f"{group_number} contains participants "
                    "from different PNB tiers."
                )

            group_tier = group_tiers.pop()

            if group_tier not in groups_by_tier:
                raise ValueError(
                    f"Planned group {group_number} has "
                    f"an invalid tier: {group_tier}."
                )

            groups_by_tier[
                group_tier
            ].append(group_number)

        for tier in [
            "low",
            "middle",
            "high",
        ]:
            group_numbers = groups_by_tier[tier]

            number_injunctive = (
                len(group_numbers) // 2
            )

            assignments = (
                [True] * number_injunctive
                + [False] * (
                    len(group_numbers)
                    - number_injunctive
                )
            )

            random.shuffle(group_numbers)
            random.shuffle(assignments)

            for group_number, show_feedback in zip(
                group_numbers,
                assignments,
            ):
                feedback_by_group[
                    group_number
                ] = show_feedback

    elif composition == "heterogeneous":

        group_numbers = list(
            range(
                1,
                len(matrix) + 1,
            )
        )

        number_injunctive = (
            len(group_numbers) // 2
        )

        assignments = (
            [True] * number_injunctive
            + [False] * (
                len(group_numbers)
                - number_injunctive
            )
        )

        random.shuffle(group_numbers)
        random.shuffle(assignments)

        for group_number, show_feedback in zip(
            group_numbers,
            assignments,
        ):
            feedback_by_group[
                group_number
            ] = show_feedback

    else:
        raise ValueError(
            f"Unknown composition: {composition}"
        )

    return feedback_by_group

def plan_game_1_groups(
    players,
    session,
):
    """
    Create the complete game-1 group plan for the selected
    participants.
    """

    if len(players) != Constants.target_players:
        raise ValueError(
            f"Expected {Constants.target_players} selected "
            f"participants, but received {len(players)}."
        )

    regime = get_regime(session, game_number=1)
    composition = get_composition(session, game_number=1)

    tier_variable = get_tier_variable(
        regime
    )

    pnb_variable = get_pnb_variable(
        regime
    )

    print(
        "\n=== PLANNING GAME 1 GROUPS ==="
    )

    print(f"Regime: {regime}")
    print(f"Composition: {composition}")
    print(f"PNB variable: {pnb_variable}")
    print(f"Tier variable: {tier_variable}")

    for player in players:
        if not player.participant.vars.get(
            "selected_for_game",
            False,
        ):
            raise ValueError(
                f"Player {player.id_in_subsession} reached "
                "game 1 without being selected."
            )

        tier = player.participant.vars.get(
            tier_variable
        )

        if tier not in [
            "low",
            "middle",
            "high",
        ]:
            raise ValueError(
                f"Player {player.id_in_subsession} "
                f"has no valid {tier_variable}."
            )

        print(
            f"Player "
            f"{player.id_in_subsession} | "
            f"PNB: "
            f"{player.participant.vars.get(pnb_variable)} | "
            f"tier: {tier}"
        )

    if composition == "homogeneous":
        matrix = create_homogeneous_groups(
            players,
            tier_variable,
        )

    elif composition == "heterogeneous":
        matrix = create_heterogeneous_groups(
            players,
            tier_variable,
        )

    else:
        raise ValueError(
            f"Unknown composition: {composition}"
        )

    expected_groups = (
        Constants.target_players
        // Constants.players_per_group
    )

    if len(matrix) != expected_groups:
        raise ValueError(
            f"Expected {expected_groups} groups, "
            f"but created {len(matrix)}."
        )

    feedback_by_group = plan_feedback_conditions(
        matrix=matrix,
        composition=composition,
        tier_variable=tier_variable,
    )

    for group_number, group_players in enumerate(
        matrix,
        start=1,
    ):
        show_feedback = feedback_by_group[
            group_number
        ]

        member_ids = [
            player.id_in_subsession
            for player in group_players
        ]

        for player in group_players:
            player.participant.vars[
                "game_1_planned_group"
            ] = group_number

            player.participant.vars[
                "game_1_feedback"
            ] = show_feedback

            player.participant.vars[
                "game_1_group_members"
            ] = member_ids

        print(
            f"Planned group {group_number} | "
            f"injunctive feedback: {show_feedback} | "
            f"members: {member_ids}"
        )

    session.vars[
        "game_1_groups_planned"
    ] = True

    print(
        "=== GAME 1 GROUP PLAN COMPLETE ===\n"
    )

def group_by_arrival_time_method(
    subsession,
    waiting_players,
):
    """
    Wait until all selected participants have reached game 1,
    plan all groups, and release each planned group of six.
    """

    if subsession.round_number != 1:
        return None

    session = subsession.session

    unselected_players = [
        player.id_in_subsession
        for player in waiting_players
        if not player.participant.vars.get(
            "selected_for_game",
            False,
        )
    ]

    if unselected_players:
        raise ValueError(
            "Non-selected participants reached game 1: "
            f"{unselected_players}"
        )

    if not session.vars.get(
        "game_1_groups_planned",
        False,
    ):
        if (
            len(waiting_players)
            < Constants.target_players
        ):
            return None

        if (
            len(waiting_players)
            > Constants.target_players
        ):
            raise ValueError(
                f"More than {Constants.target_players} "
                "selected participants reached game 1."
            )

        plan_game_1_groups(
            players=list(waiting_players),
            session=session,
        )

    planned_group_numbers = sorted({
        player.participant.vars.get(
            "game_1_planned_group"
        )
        for player in waiting_players
        if player.participant.vars.get(
            "game_1_planned_group"
        ) is not None
    })

    for planned_group_number in (
        planned_group_numbers
    ):
        group_players = [
            player
            for player in waiting_players
            if player.participant.vars.get(
                "game_1_planned_group"
            ) == planned_group_number
        ]

        if (
            len(group_players)
            == Constants.players_per_group
        ):
            return group_players

    return None


def initialize_game_1_group(group):
    """
    Copy the planned treatment information to the actual
    oTree group in all rounds.
    """

    players = group.get_players()
    session = group.subsession.session

    regime = get_regime(session, game_number=1)
    composition = get_composition(session, game_number=1)

    planned_group_numbers = {
        player.participant.vars.get(
            "game_1_planned_group"
        )
        for player in players
    }

    if len(planned_group_numbers) != 1:
        raise ValueError(
            f"Actual group {group.id_in_subsession} "
            "contains players from different planned groups."
        )

    planned_group_number = (
        planned_group_numbers.pop()
    )

    feedback_conditions = {
        player.participant.vars.get(
            "game_1_feedback"
        )
        for player in players
    }

    if len(feedback_conditions) != 1:
        raise ValueError(
            f"Actual group {group.id_in_subsession} "
            "contains inconsistent feedback assignments."
        )

    show_feedback = (
        feedback_conditions.pop()
    )

    member_ids = [
        player.id_in_subsession
        for player in players
    ]

    for round_number in range(
        1,
        Constants.num_rounds + 1,
    ):
        group_in_round = group.in_round(
            round_number
        )

        group_in_round.show_feedback = (
            show_feedback
        )

        group_in_round.regime = regime

        group_in_round.composition = (
            composition
        )

    for player in players:
        player.participant.vars[
            "game_1_group_members"
        ] = member_ids

    print(
        f"Actual group {group.id_in_subsession} | "
        f"planned group: {planned_group_number} | "
        f"regime: {regime} | "
        f"composition: {composition} | "
        f"injunctive feedback: {show_feedback} | "
        f"members: {member_ids}"
    )


# ============================================================
# PAGES
# ============================================================

class IntroductionPage(Page):
    timeout_seconds = it
    timer_text = "Time remaining:"

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player):
        return dict(
            regime=player.group.regime,
            other_players=(
                Constants.players_per_group - 1
            ),
            players_per_group=(
                Constants.players_per_group
            ),
            num_rounds=Constants.num_rounds,
            endowment=Constants.endowment,
            efficiency_factor=(
                Constants.efficiency_factor
            ),
            threshold=Constants.threshold,
            reward=int(Constants.reward),
        )

class GroupFormationWaitPage(WaitPage):
    """
    Wait until the 72 selected participants have arrived,
    create the planned groups, and release each group of six.
    """

    group_by_arrival_time = True

    title_text = "Waiting for your group"

    body_text = (
        "Please keep this page open and remain on this tab. "
        "The game will begin when your group is ready."
    )

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def after_all_players_arrive(group):
        initialize_game_1_group(group)

class Contribution(Page):
    form_model = "player"
    form_fields = ["public_investment"]

    timeout_seconds = ct

    @staticmethod
    def before_next_page(
            player,
            timeout_happened,
    ):
        handle_contribution_timeout(
            player=player,
            timeout_happened=timeout_happened,
        )

    @staticmethod
    def vars_for_template(player):
        return dict(
            round_number=player.round_number,
            num_rounds=Constants.num_rounds,
            endowment=Constants.endowment,
            efficiency_factor=Constants.efficiency_factor,
            threshold=Constants.threshold,
            reward=int(Constants.reward),
            regime=player.group.regime,
            composition=player.group.composition,
        )

class GroupWaitPage(WaitPage):

    title_text = "Please wait"

    body_text = (
        "Waiting for the other members of your group "
        "to make their decision."
    )

    @staticmethod
    def after_all_players_arrive(group):
        group.set_payoffs()


class ObservationPage(Page):

    timeout_seconds = ot

    @staticmethod
    def vars_for_template(player):
        group = player.group
        players = group.get_players()

        average_public = round(
            sum(
                float(p.public_investment)
                for p in players
            ) / len(players),
            2,
        )

        average_private = round(
            sum(
                float(p.payoff_from_private)
                for p in players
            ) / len(players),
            2,
        )

        average_total = round(
            sum(
                float(p.gross_profit)
                for p in players
            ) / len(players),
            2,
        )

        round_data = []

        for group_player in players:
            if group.show_feedback:
                injunctive_feedback = (
                    get_injunctive_feedback(
                        regime=group.regime,
                        contribution=group_player.public_investment,
                    )
                )
            else:
                injunctive_feedback = None

            round_data.append(
                dict(
                    public=(
                        group_player.public_investment
                    ),
                    private=(
                        group_player.payoff_from_private
                    ),
                    total=(
                        group_player.gross_profit
                    ),
                    evaluation=(
                        injunctive_feedback[
                            "evaluation"
                        ]
                        if injunctive_feedback
                        else None
                    ),
                    evaluation_message=(
                        injunctive_feedback["message"]
                        if injunctive_feedback
                        else None
                    ),
                )
            )

        table_data = [
            dict(
                round_number=player.round_number,
                round_data=round_data,
                group_avg=dict(
                    public=average_public,
                    private=average_private,
                    total=average_total,
                ),
            )
        ]

        return dict(
            round_number=player.round_number,
            num_rounds=Constants.num_rounds,
            table_data=table_data,
            player_id=player.id_in_group,
            show_feedback=group.show_feedback,
            average=average_public,
            regime=group.regime,
            composition=group.composition,
        )


page_sequence = [
    GroupFormationWaitPage,
    IntroductionPage,
    Contribution,
    GroupWaitPage,
    ObservationPage,
]