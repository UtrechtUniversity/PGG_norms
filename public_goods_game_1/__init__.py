from otree.api import *
import random


doc = """
First public goods game.

Participants are assigned to six-person groups based on their
personal normative beliefs. The game type and group composition
are determined by the session-level treatment conditions.
"""


from settings import (
    players_per_group as ppp,
    efficiency_factor as ef,
    num_rounds as nr,
)


class Constants(BaseConstants):
    name_in_url = "public_goods_game_1"
    players_per_group = ppp
    num_rounds = nr

    num_recent_rounds_to_display = 1

    endowment = 20

    # Linear game
    efficiency_factor = ef

    # Stepwise game
    threshold = 60
    reward = 15


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



def get_regime(session):
    """
    Return the game played in public_goods_game_1.
    """

    regime = session.config[
        "public_goods_first"
    ]

    if regime not in [
        "linear",
        "stepwise",
    ]:
        raise ValueError(
            "public_goods_first must be "
            "'linear' or 'stepwise'."
        )

    return regime


def get_composition(session):
    """
    Return the composition condition used in
    public_goods_game_1.
    """

    composition = session.config[
        "composition_first"
    ]

    if composition not in [
        "homogeneous",
        "heterogeneous",
    ]:
        raise ValueError(
            "composition_first must be "
            "'homogeneous' or 'heterogeneous'."
        )

    return composition


def get_tier_variable(regime):
    """
    Return the PNB tier belonging to the current game.
    """

    if regime == "linear":
        return "pnb_tier_linear"

    if regime == "stepwise":
        return "pnb_tier_stepwise"

    raise ValueError(
        f"Unknown regime: {regime}"
    )


def get_pnb_variable(regime):
    """
    Return the PNB score belonging to the current game.
    """

    if regime == "linear":
        return "pnb_linear"

    if regime == "stepwise":
        return "pnb_stepwise"

    raise ValueError(
        f"Unknown regime: {regime}"
    )




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


def assign_feedback_conditions(
    subsession,
    regime,
    composition,
):
    """
    Assign feedback at the group level.

    For homogeneous groups, randomize feedback separately
    within each PNB tier.

    For heterogeneous groups, randomize feedback across all
    groups because every group has the same tier composition.
    """

    groups = subsession.get_groups()
    tier_variable = get_tier_variable(regime)

    def save_assignment(
        group,
        show_feedback,
    ):
        group_members = group.get_players()

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

        for player in group_members:
            player.participant.vars[
                "game_1_feedback"
            ] = show_feedback

            player.participant.vars[
                "game_1_group_members"
            ] = [
                other.id_in_subsession
                for other in group_members
            ]

        print(
            f"Group {group.id_in_subsession} | "
            f"regime: {regime} | "
            f"composition: {composition} | "
            f"injunctive feedback: "
            f"{show_feedback} | "
            f"members: "
            f"{[p.id_in_subsession for p in group_members]}"
        )

    if composition == "homogeneous":

        groups_by_tier = {
            "low": [],
            "middle": [],
            "high": [],
        }

        for group in groups:
            group_members = group.get_players()

            group_tiers = {
                player.participant.vars.get(
                    tier_variable
                )
                for player in group_members
            }

            if len(group_tiers) != 1:
                raise ValueError(
                    f"Homogeneous group "
                    f"{group.id_in_subsession} contains "
                    "participants from different PNB tiers."
                )

            group_tier = group_tiers.pop()

            groups_by_tier[
                group_tier
            ].append(group)

        for tier in [
            "low",
            "middle",
            "high",
        ]:
            tier_groups = groups_by_tier[tier]
            number_of_groups = len(tier_groups)

            number_injunctive = (
                number_of_groups // 2
            )

            assignments = (
                [True] * number_injunctive
                + [False] * (
                    number_of_groups
                    - number_injunctive
                )
            )

            random.shuffle(assignments)
            random.shuffle(tier_groups)

            for group, show_feedback in zip(
                tier_groups,
                assignments,
            ):
                save_assignment(
                    group,
                    show_feedback,
                )

    elif composition == "heterogeneous":

        number_of_groups = len(groups)

        number_injunctive = (
            number_of_groups // 2
        )

        assignments = (
            [True] * number_injunctive
            + [False] * (
                number_of_groups
                - number_injunctive
            )
        )

        random.shuffle(assignments)

        for group, show_feedback in zip(
            groups,
            assignments,
        ):
            save_assignment(
                group,
                show_feedback,
            )

    else:
        raise ValueError(
            f"Unknown composition: {composition}"
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
            reward=Constants.reward,
        )

class GroupFormationWaitPage(WaitPage):
    """
    Wait until all participants have completed the PNB
    elicitation and then create all game-1 groups.
    """

    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def after_all_players_arrive(
        subsession
    ):
        session = subsession.session
        players = subsession.get_players()

        regime = get_regime(session)
        composition = get_composition(session)

        tier_variable = get_tier_variable(
            regime
        )

        pnb_variable = get_pnb_variable(
            regime
        )

        print(
            "\n=== GAME 1 GROUP FORMATION ==="
        )

        print(f"Regime: {regime}")
        print(f"Composition: {composition}")
        print(f"PNB variable: {pnb_variable}")
        print(f"Tier variable: {tier_variable}")

        for player in players:
            print(
                f"Player "
                f"{player.id_in_subsession} | "
                f"PNB: "
                f"{player.participant.vars.get(pnb_variable)} | "
                f"tier: "
                f"{player.participant.vars.get(tier_variable)}"
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
                f"Unknown composition: "
                f"{composition}"
            )

        subsession.set_group_matrix(matrix)

        # Keep these groups together in rounds 2-10.
        for round_number in range(
            2,
            Constants.num_rounds + 1,
        ):
            subsession.in_round(
                round_number
            ).group_like_round(1)

        assign_feedback_conditions(
            subsession=subsession,
            regime=regime,
            composition=composition,
        )

        print(
            "=== GAME 1 GROUP FORMATION COMPLETE ===\n"
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