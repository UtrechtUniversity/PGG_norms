"""
helper functions for the two public-goods-game apps.
"""

import random

from settings import (
    endowment,
    players_per_group,
    efficiency_factor,
    threshold,
    reward,
)


def handle_contribution_timeout(
    player,
    timeout_happened,
):
    """
    Record whether the contribution page timed out and, when it
    did, provide a contribution so the group can continue.

    The previous contribution in the same game is reused whenever
    available. In the first round, or when no previous contribution
    exists, a random integer contribution is generated.
    """

    player.contribution_timed_out = (
        timeout_happened
    )

    if not timeout_happened:
        return

    fallback_contribution = None

    if player.round_number > 1:
        previous_player = player.in_round(
            player.round_number - 1
        )

        fallback_contribution = (
            previous_player.public_investment
        )

    if fallback_contribution is None:
        fallback_contribution = random.randint(
            0,
            int(endowment),
        )

    player.public_investment = (
        fallback_contribution
    )

def set_payoffs(group):
    """
    Calculate and store all player payoffs for one round.
    """

    players = group.get_players()

    group.total_group_investment = sum(
        player.public_investment
        for player in players
    )

    for player in players:
        player.payoff_from_private = (
            endowment
            - player.public_investment
        )

        if group.regime == "linear":
            player.payoff_from_public = (
                efficiency_factor
                * group.total_group_investment
            )

        elif group.regime == "stepwise":
            threshold_met = (
                group.total_group_investment
                >= threshold
            )

            if threshold_met:
                player.payoff_from_public = reward
            else:
                player.payoff_from_public = 0

        else:
            raise ValueError(
                f"Unknown regime: {group.regime}"
            )

        player.gross_profit = (
            player.payoff_from_private
            + player.payoff_from_public
        )

        if player.contribution_timed_out:
            player.payoff = 0 # don't save payoffs when timed out
        else:
            player.payoff = player.gross_profit

def get_regime(session, game_number):
    """
    Return the production function used in PGG1 or PGG2.
    PGG2 always uses the production function not used in PGG1.
    """

    first_regime = session.config[
        "public_goods_first"
    ]

    if first_regime not in [
        "linear",
        "stepwise",
    ]:
        raise ValueError(
            "public_goods_first must be "
            "'linear' or 'stepwise'."
        )

    if game_number == 1:
        return first_regime

    if game_number == 2:
        if first_regime == "linear":
            return "stepwise"

        return "linear"

    raise ValueError(
        f"Unknown game number: {game_number}. "
        "Expected 1 or 2."
    )


def get_composition(session, game_number):
    """
    Return the composition condition used in PGG1 or PGG2.
    PGG2 always uses the composition condition not used in PGG1.
    """

    first_composition = session.config[
        "composition_first"
    ]

    if first_composition not in [
        "homogeneous",
        "heterogeneous",
    ]:
        raise ValueError(
            "composition_first must be "
            "'homogeneous' or 'heterogeneous'."
        )

    if game_number == 1:
        return first_composition

    if game_number == 2:
        if first_composition == "homogeneous":
            return "heterogeneous"

        return "homogeneous"

    raise ValueError(
        f"Unknown game number: {game_number}. "
        "Expected 1 or 2."
    )


def get_tier_variable(regime):
    """
    Return the participant-variable name containing the PNB tier
    for the specified production function.
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
    Return the participant-variable name containing the PNB score
    for the specified production function.
    """

    if regime == "linear":
        return "pnb_linear"

    if regime == "stepwise":
        return "pnb_stepwise"

    raise ValueError(
        f"Unknown regime: {regime}"
    )


def get_injunctive_feedback(regime, contribution):
    """
    Return the evaluation category and message for a contribution.

    Stepwise game:
    - Below the equal-share threshold contribution: disapproval.
    - At or above the equal-share contribution: strong approval.

    Linear game:
    - Below the equal-share contribution: disapproval.
    - From the equal-share contribution through the upper bound:
      moderate approval.
    - Above the upper bound: strong approval.
    """

    contribution = float(contribution)

    disapproval = dict(
        evaluation="disapproved",
        message=(
            "Most players indicated that a higher "
            "contribution would be appropriate."
        ),
    )

    moderate_approval = dict(
        evaluation="moderately_approved",
        message=(
            "Some players indicated that this "
            "contribution is appropriate."
        ),
    )

    strong_approval = dict(
        evaluation="strongly_approved",
        message=(
            "Most players indicated that this "
            "contribution is appropriate."
        ),
    )

    equal_share = (
        float(threshold)
        / players_per_group
    )

    linear_upper_bound = (
        equal_share
        * players_per_group
        * efficiency_factor
    )

    if regime == "stepwise":
        if contribution >= equal_share:
            return strong_approval

        return disapproval

    if regime == "linear":
        if contribution < equal_share:
            return disapproval

        if contribution <= linear_upper_bound:
            return moderate_approval

        return strong_approval

    raise ValueError(
        f"Unknown regime: {regime}"
    )
