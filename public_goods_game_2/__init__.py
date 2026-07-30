from otree.api import *
import random


doc = """
Second public goods game.

Participants are dynamically assigned to new groups based on
their personal normative beliefs. The second game uses the other
game type and composition condition relative to the first game.

Repeated groupmate pairs from game 1 are minimized
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


class Constants(BaseConstants):
    name_in_url = "public_goods_game_2"
    players_per_group = ppp
    num_rounds = nr

    num_recent_rounds_to_display = 1

    endowment = e

    # Linear game
    efficiency_factor = ef

    # Stepwise game
    threshold = t
    reward = r

    # Number of randomly generated valid groups considered
    # when minimizing repeated PGG1 groupmates.
    grouping_attempts = 1000


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
        players = self.get_players()

        self.total_group_investment = sum(
            p.public_investment
            for p in players
        )

        for p in players:
            p.payoff_from_private = (
                Constants.endowment
                - p.public_investment
            )

            if self.regime == "linear":
                p.payoff_from_public = (
                    Constants.efficiency_factor
                    * self.total_group_investment
                )

            elif self.regime == "stepwise":
                threshold_met = (
                    self.total_group_investment
                    >= Constants.threshold
                )

                if threshold_met:
                    p.payoff_from_public = (
                        Constants.reward
                    )
                else:
                    p.payoff_from_public = 0

            else:
                raise ValueError(
                    f"Unknown regime: {self.regime}"
                )

            p.gross_profit = (
                p.payoff_from_private
                + p.payoff_from_public
            )

            p.payoff = p.gross_profit


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


def creating_session(subsession):
    if subsession.round_number != 1:
        return

    session = subsession.session
    number_of_players = np
    group_size = Constants.players_per_group

    if number_of_players % group_size != 0:
        raise ValueError(
            f"The number of participants "
            f"({number_of_players}) is not divisible "
            f"by the group size ({group_size})."
        )

    number_of_groups = (
        number_of_players // group_size
    )

    composition = get_composition(session)

    # --------------------------------------------------------
    # Homogeneous:
    # balance feedback separately within each PNB tier.
    # --------------------------------------------------------

    if composition == "homogeneous":

        if number_of_players % 3 != 0:
            raise ValueError(
                f"The number of participants "
                f"({number_of_players}) must be "
                "divisible by 3."
            )

        players_per_tier = (
            number_of_players // 3
        )

        if players_per_tier % group_size != 0:
            raise ValueError(
                f"Each PNB tier contains "
                f"{players_per_tier} participants, "
                f"which is not divisible by the "
                f"group size ({group_size})."
            )

        groups_per_tier = (
            players_per_tier // group_size
        )

        feedback_by_tier = {}

        for tier in [
            "low",
            "middle",
            "high",
        ]:
            number_injunctive = (
                groups_per_tier // 2
            )

            assignments = (
                [True] * number_injunctive
                + [False] * (
                    groups_per_tier
                    - number_injunctive
                )
            )

            random.shuffle(assignments)

            feedback_by_tier[tier] = (
                assignments
            )

        session.vars[
            "game_2_feedback_by_tier"
        ] = feedback_by_tier

    # --------------------------------------------------------
    # Heterogeneous:
    # balance feedback across all groups.
    # --------------------------------------------------------

    elif composition == "heterogeneous":

        number_injunctive = (
            number_of_groups // 2
        )

        feedback_assignments = (
            [True] * number_injunctive
            + [False] * (
                number_of_groups
                - number_injunctive
            )
        )

        random.shuffle(feedback_assignments)

        session.vars[
            "game_2_feedback_assignments"
        ] = feedback_assignments

    else:
        raise ValueError(
            f"Unknown composition: {composition}"
        )

    session.vars[
        "next_game_2_group_number"
    ] = 1

    session.vars[
        "game_2_total_players"
    ] = number_of_players

    session.vars[
        "game_2_players_grouped"
    ] = 0


def get_regime(session):
    """
    PGG2 uses the other game type.
    """

    first_regime = session.config[
        "public_goods_first"
    ]

    if first_regime == "linear":
        return "stepwise"

    if first_regime == "stepwise":
        return "linear"

    raise ValueError(
        "public_goods_first must be "
        "'linear' or 'stepwise'."
    )


def get_composition(session):
    """
    PGG2 uses the other composition condition.
    """

    first_composition = session.config[
        "composition_first"
    ]

    if first_composition == "homogeneous":
        return "heterogeneous"

    if first_composition == "heterogeneous":
        return "homogeneous"

    raise ValueError(
        "composition_first must be "
        "'homogeneous' or 'heterogeneous'."
    )


def get_tier_variable(regime):
    if regime == "linear":
        return "pnb_tier_linear"

    if regime == "stepwise":
        return "pnb_tier_stepwise"

    raise ValueError(
        f"Unknown regime: {regime}"
    )


def get_pnb_variable(regime):
    if regime == "linear":
        return "pnb_linear"

    if regime == "stepwise":
        return "pnb_stepwise"

    raise ValueError(
        f"Unknown regime: {regime}"
    )



def were_groupmates_in_game_1(
    player_a,
    player_b,
):
    """
    Return True if two participants were members
    of the same group in PGG1.
    """

    previous_group_members = (
        player_a.participant.vars.get(
            "game_1_group_members",
            [],
        )
    )

    return (
        player_b.id_in_subsession
        in previous_group_members
    )


def calculate_previous_overlap(players):
    """
    Count the number of participant pairs that already
    played together in PGG1.

    Score 0 means that no two participants were previously
    groupmates.
    """

    overlap = 0

    for first_position in range(
        len(players)
    ):
        for second_position in range(
            first_position + 1,
            len(players),
        ):
            player_a = players[
                first_position
            ]

            player_b = players[
                second_position
            ]

            if were_groupmates_in_game_1(
                player_a,
                player_b,
            ):
                overlap += 1

    return overlap


def select_best_candidate(
    candidate_groups,
):
    """
    Return the candidate group with the fewest repeated
    PGG1 groupmate pairs.
    """

    if not candidate_groups:
        return None

    scored_groups = [
        (
            calculate_previous_overlap(
                candidate
            ),
            candidate,
        )
        for candidate in candidate_groups
    ]

    lowest_overlap = min(
        score
        for score, candidate
        in scored_groups
    )

    best_groups = [
        candidate
        for score, candidate
        in scored_groups
        if score == lowest_overlap
    ]

    selected_group = random.choice(
        best_groups
    )

    random.shuffle(selected_group)

    return selected_group



def select_homogeneous_group(
    waiting_players,
    tier_variable,
):
    """
    Create a group from a single PNB tier while minimizing
    repeated PGG1 groupmate pairs.
    """

    group_size = Constants.players_per_group
    candidate_groups = []

    for tier in [
        "low",
        "middle",
        "high",
    ]:
        eligible_players = [
            player
            for player in waiting_players
            if player.participant.vars.get(
                tier_variable
            ) == tier
        ]

        if len(eligible_players) < group_size:
            continue

        if len(eligible_players) == group_size:
            candidate_groups.append(
                list(eligible_players)
            )

        else:
            for attempt in range(
                Constants.grouping_attempts
            ):
                candidate_groups.append(
                    random.sample(
                        eligible_players,
                        group_size,
                    )
                )

    return select_best_candidate(
        candidate_groups
    )


def select_heterogeneous_group(
    waiting_players,
    tier_variable,
):
    """
    Create a group containing equal numbers of low,
    middle, and high-PNB participants while minimizing
    repeated PGG1 groupmate pairs.

    Group size 3:
    one low, one middle, and one high.

    Group size 6:
    two low, two middle, and two high.
    """

    group_size = Constants.players_per_group

    if group_size % 3 != 0:
        raise ValueError(
            f"The group size ({group_size}) must be "
            "divisible by 3 to create heterogeneous groups."
        )

    number_per_tier = group_size // 3

    players_by_tier = {
        "low": [],
        "middle": [],
        "high": [],
    }

    for player in waiting_players:
        tier = player.participant.vars.get(
            tier_variable
        )

        if tier in players_by_tier:
            players_by_tier[tier].append(
                player
            )

    enough_players = all(
        len(players_by_tier[tier])
        >= number_per_tier
        for tier in [
            "low",
            "middle",
            "high",
        ]
    )

    if not enough_players:
        return None

    candidate_groups = []

    for attempt in range(
        Constants.grouping_attempts
    ):
        candidate = []

        for tier in [
            "low",
            "middle",
            "high",
        ]:
            candidate.extend(
                random.sample(
                    players_by_tier[tier],
                    number_per_tier,
                )
            )

        candidate_groups.append(candidate)

    return select_best_candidate(
        candidate_groups
    )


def enough_players_are_waiting(
    subsession,
    waiting_players,
):
    """
    Normally wait until three groups' worth of participants
    is available.

    When fewer than three groups remain, wait until all
    remaining participants have arrived.
    """

    session = subsession.session

    total_players = session.vars[
        "game_2_total_players"
    ]

    players_grouped = session.vars.get(
        "game_2_players_grouped",
        0,
    )

    players_remaining = (
        total_players - players_grouped
    )

    preferred_waiting_pool = min(
        3 * Constants.players_per_group, #wait for 18 players to be ready (3 groups).
        players_remaining,
    )

    return (
        len(waiting_players)
        >= preferred_waiting_pool
    )


def group_by_arrival_time_method(
    subsession,
    waiting_players,
):
    """
    Form a valid group from the current pool of waiting
    participants.

    Former PGG1 groupmates are minimized but never
    prohibited.
    """

    if not enough_players_are_waiting(
        subsession,
        waiting_players,
    ):
        return None

    regime = get_regime(
        subsession.session
    )

    composition = get_composition(
        subsession.session
    )

    tier_variable = get_tier_variable(
        regime
    )

    if composition == "homogeneous":
        return select_homogeneous_group(
            waiting_players,
            tier_variable,
        )

    if composition == "heterogeneous":
        return select_heterogeneous_group(
            waiting_players,
            tier_variable,
        )

    raise ValueError(
        f"Unknown composition: {composition}"
    )



def take_feedback_assignment(
    session,
    group,
):
    """
    Return the next randomized feedback assignment.

    For homogeneous groups, feedback is balanced separately
    within the low, middle, and high PNB tiers.

    For heterogeneous groups, feedback is balanced across
    all groups.
    """

    regime = get_regime(session)
    composition = get_composition(session)

    if composition == "homogeneous":
        tier_variable = get_tier_variable(
            regime
        )

        group_tiers = {
            player.participant.vars.get(
                tier_variable
            )
            for player in group.get_players()
        }

        if len(group_tiers) != 1:
            raise ValueError(
                f"Homogeneous group "
                f"{group.id_in_subsession} contains "
                "participants from different PNB tiers."
            )

        group_tier = group_tiers.pop()

        if group_tier not in [
            "low",
            "middle",
            "high",
        ]:
            raise ValueError(
                f"Group {group.id_in_subsession} "
                f"has an invalid PNB tier: "
                f"{group_tier}."
            )

        feedback_by_tier = session.vars.get(
            "game_2_feedback_by_tier",
            {},
        )

        assignments = feedback_by_tier.get(
            group_tier,
            [],
        )

        if not assignments:
            raise ValueError(
                f"No game-2 feedback assignments "
                f"remain for the {group_tier} tier."
            )

        show_feedback = assignments.pop(0)

        feedback_by_tier[
            group_tier
        ] = assignments

        session.vars[
            "game_2_feedback_by_tier"
        ] = feedback_by_tier

        return show_feedback

    if composition == "heterogeneous":
        assignments = session.vars.get(
            "game_2_feedback_assignments",
            [],
        )

        if not assignments:
            raise ValueError(
                "No heterogeneous game-2 feedback "
                "assignments remain."
            )

        show_feedback = assignments.pop(0)

        session.vars[
            "game_2_feedback_assignments"
        ] = assignments

        return show_feedback

    raise ValueError(
        f"Unknown composition: {composition}"
    )


def copy_group_to_future_rounds(group):
    """
    Keep the dynamically formed group together
    in rounds 2-10.
    """

    current_players = group.get_players()

    for round_number in range(
        2,
        Constants.num_rounds + 1,
    ):
        future_players = [
            player.in_round(round_number)
            for player in current_players
        ]

        future_group = group.in_round(
            round_number
        )

        future_group.set_players(
            future_players
        )


def set_group_conditions_in_all_rounds(
    group,
    regime,
    composition,
    show_feedback,
):
    """
    Store the experimental conditions in every round.
    """

    for round_number in range(
        1,
        Constants.num_rounds + 1,
    ):
        group_in_round = group.in_round(
            round_number
        )

        group_in_round.regime = regime

        group_in_round.composition = (
            composition
        )

        group_in_round.show_feedback = (
            show_feedback
        )


# ============================================================
# PAGES
# ============================================================


class IntroductionPage(Page):
    timeout_seconds = 600
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
    Dynamically form a new group for PGG2.
    """

    group_by_arrival_time = True

    title_text = "Please wait"

    body_text = (
        "You have completed the first game. "
        "Please wait while we form your group for the second game. "
        "This may take a few minutes."
    )

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def after_all_players_arrive(group):
        session = group.session

        regime = get_regime(session)
        composition = get_composition(session)

        show_feedback = (
            take_feedback_assignment(
                session,
                group,
            )
        )

        game_2_group_number = session.vars.get(
            "next_game_2_group_number",
            1,
        )

        session.vars[
            "next_game_2_group_number"
        ] = game_2_group_number + 1

        group_members = group.get_players()

        session.vars[
            "game_2_players_grouped"
        ] = (
            session.vars.get(
                "game_2_players_grouped",
                0,
            )
            + len(group_members)
        )

        previous_overlap = (
            calculate_previous_overlap(
                group_members
            )
        )

        for player in group_members:
            player.participant.vars[
                "game_2_group_number"
            ] = game_2_group_number

            player.participant.vars[
                "game_2_feedback"
            ] = show_feedback

            player.participant.vars[
                "game_2_group_members"
            ] = [
                other.id_in_subsession
                for other in group_members
            ]

        copy_group_to_future_rounds(group)

        set_group_conditions_in_all_rounds(
            group=group,
            regime=regime,
            composition=composition,
            show_feedback=show_feedback,
        )

        tier_variable = get_tier_variable(
            regime
        )

        pnb_variable = get_pnb_variable(
            regime
        )

        print(
            "\n=== GAME 2 GROUP FORMED ==="
        )

        print(
            f"Game-2 group number: "
            f"{game_2_group_number}"
        )

        print(f"Regime: {regime}")
        print(f"Composition: {composition}")

        print(
            f"Injunctive feedback: "
            f"{show_feedback}"
        )

        print(
            f"Repeated PGG1 groupmate pairs: "
            f"{previous_overlap}"
        )

        for player in group_members:
            print(
                f"Player "
                f"{player.id_in_subsession} | "
                f"PNB: "
                f"{player.participant.vars.get(pnb_variable)} | "
                f"tier: "
                f"{player.participant.vars.get(tier_variable)}"
            )

        print(
            "=== GAME 2 GROUP FORMATION COMPLETE ===\n"
        )


class Contribution(Page):
    form_model = "player"
    form_fields = ["public_investment"]

    @staticmethod
    def vars_for_template(player):
        return dict(
            round_number=player.round_number,
            num_rounds=Constants.num_rounds,
            endowment=Constants.endowment,
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
                evaluation = (
                    "approved"
                    if group_player.public_investment
                    >= average_public
                    else "disapproved"
                )

            else:
                evaluation = None

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
                    evaluation=evaluation,
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