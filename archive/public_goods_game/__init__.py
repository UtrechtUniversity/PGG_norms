from otree.api import *
import random

doc = """
Public goods game with descriptive/injunctive norm feedback
"""

from settings import (
    players_per_group as ppp,
    efficiency_factor as ef,
    num_rounds as nr,
)

class Constants(BaseConstants):
    name_in_url = "public_goods_game"
    players_per_group = ppp
    num_rounds = nr
    num_recent_rounds_to_display = 1

    endowment = 20
    # linear game
    efficiency_factor = ef
    # stepwise game
    threshold = 40
    reward = 30

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_group_investment = models.CurrencyField(initial=0)
    show_feedback = models.BooleanField(initial=True)  # group-level stimulus

    def set_payoffs(self, regime):
        players = self.get_players()
        self.total_group_investment = sum(p.public_investment for p in players)

        for p in players:
            p.payoff_from_private = Constants.endowment - p.public_investment

            if regime == "linear":
                p.payoff_from_public = Constants.efficiency_factor * self.total_group_investment

            elif regime == "stepwise":
                threshold_met = self.total_group_investment >= Constants.threshold
                p.payoff_from_public = Constants.reward if threshold_met else 0

            else:
                raise ValueError("Unknown regime")

            p.gross_profit = p.payoff_from_private + p.payoff_from_public
            p.participant.payoff = p.gross_profit

class Player(BasePlayer):
    payoff_from_private = models.CurrencyField()
    payoff_from_public = models.CurrencyField()
    gross_profit = models.CurrencyField(initial=0)

    public_investment = models.CurrencyField(
        min=0,
        max=Constants.endowment,
        verbose_name="How much would you like to invest in the public account?",
    )


# ======================
# PAGES
# ======================

class IntroductionPage(Page):
    def is_displayed(self):
        return self.round_number == 1


class GroupFormationWaitPage(WaitPage):
    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number == 1

    def after_all_players_arrive(self):
        subsession = self.subsession
        players = subsession.get_players()

        print("\n=== GROUP FORMATION START ===\n")

        # Print players + PNB
        print("Players and PNBs:")
        for p in players:
            print(f"Player {p.id_in_subsession} | PNB: {p.participant.vars.get('pnb')}")

        # Sort players by PNB
        players_sorted = sorted(players, key=lambda p: p.participant.vars.get('pnb', 0))
        print("\nSorted players (low → high PNB):")
        for p in players_sorted:
            print(f"Player {p.id_in_subsession} | PNB: {p.participant.vars.get('pnb')}")

        group_size = Constants.players_per_group
        condition = self.session.config['condition']
        print(f"\nCondition: {condition}, Group size: {group_size}, Total players: {len(players_sorted)}")

        matrix = []

        # HOMOGENEOUS GROUPS
        if condition == 'homogeneous':
            print("\nCreating HOMOGENEOUS groups...")
            for i in range(0, len(players_sorted), group_size):
                group = players_sorted[i:i + group_size]
                matrix.append(group)
                print(f"Group {len(matrix)}: {[p.id_in_subsession for p in group]}")

        # HETEROGENEOUS GROUPS
        elif condition == 'heterogeneous':
            print("\nCreating HETEROGENEOUS groups using tiers...")
            num_groups = len(players_sorted) // group_size
            tiers = Constants.players_per_group
            tier_size = len(players_sorted) // tiers
            tiers_list = []
            for i in range(tiers):
                start = i * tier_size
                end = (i + 1) * tier_size if i < tiers - 1 else len(players_sorted)
                tiers_list.append(players_sorted[start:end])
            matrix = [[] for _ in range(num_groups)]
            for tier in reversed(tiers_list):
                for idx, player in enumerate(tier):
                    group_number = idx % num_groups
                    matrix[group_number].append(player)
            for i, group in enumerate(matrix, start=1):
                print(f"Group {i}: {[p.id_in_subsession for p in group]}")

        subsession.set_group_matrix(matrix)
        print("\nGroup matrix assigned.\n")

        # -------------------------
        # Assign group-level feedback condition (50/50)
        # -------------------------
        all_groups = subsession.get_groups()
        num_groups = len(all_groups)
        num_feedback = num_groups // 2
        assignments = [True] * num_feedback + [False] * (num_groups - num_feedback)
        random.shuffle(assignments)

        for i, (group, show) in enumerate(zip(all_groups, assignments), start=1):
            group.show_feedback = show
            for p in group.get_players():
                p.participant.vars['show_feedback'] = show
            print(f"Group {i} show_feedback: {show} | Members: {[p.id_in_subsession for p in group.get_players()]}")
        # Copy round 1 structure to all future rounds
        for r in range(2, Constants.num_rounds + 1):
            subsession.in_round(r).group_like_round(1)

        print("\n=== GROUP FORMATION END ===\n")

class Contribution(Page):
    form_model = "player"
    form_fields = ["public_investment"]

    def vars_for_template(self):
        return dict(
            round_number=self.round_number,
            endowment=Constants.endowment,
        )

class GroupWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        """
        depending on condition and round, determine payoff function (linear/stepwise)
        """
        subsession = group.subsession
        session = subsession.session
        round_number = subsession.round_number
        mid = Constants.num_rounds // 2

        first = session.config["public_goods_first"]

        if first == "linear":
            regime = "linear" if round_number <= mid else "stepwise"
        elif first == "stepwise":
            regime = "stepwise" if round_number <= mid else "linear"
        else:
            raise ValueError("Invalid config")

        group.set_payoffs(regime)

class ObservationPage(Page):
    def vars_for_template(self):
        players_in_all_rounds = [p.in_all_rounds() for p in self.group.get_players()]
        current_round = self.round_number
        first_round = max(1, current_round - Constants.num_recent_rounds_to_display + 1)

        table_data = []

        # Use persistent participant-level feedback
        show_feedback = self.participant.vars.get('show_feedback', True)

        for r in range(first_round, current_round + 1):
            round_data = []
            players_in_round = [player[r - 1] for player in players_in_all_rounds]

            avg_public = round(
                sum(float(p.public_investment) for p in players_in_round) / len(players_in_round), 2
            )
            avg_private = round(
                sum(float(p.payoff_from_private) for p in players_in_round) / len(players_in_round), 2
            )
            avg_total = round(
                sum(float(p.gross_profit) for p in players_in_round) / len(players_in_round), 2
            )

            for p in players_in_round:
                if show_feedback:
                    evaluation = "approved" if p.public_investment >= avg_public else "disapproved"
                else:
                    evaluation = None
                round_data.append({
                    'public': p.public_investment,
                    'private': p.payoff_from_private,
                    'total': p.gross_profit,
                    'evaluation': evaluation
                })

            table_data.append({
                'round_number': r,
                'round_data': round_data,
                'group_avg': {
                    'public': avg_public,
                    'private': avg_private,
                    'total': avg_total
                }
            })

        return dict(
            round_number=current_round,
            table_data=table_data,
            player_id=self.id_in_group,
            show_feedback=show_feedback,
            average = avg_public
        )

class SecondGame(Page):
    def is_displayed(self):
        mid = Constants.num_rounds // 2
        return self.round_number == mid + 1

    def vars_for_template(self):
        session = self.session
        first = session.config["public_goods_first"]

        if first == "linear":
            from_phase = "linear"
            to_phase = "stepwise"
        else:
            from_phase = "stepwise"
            to_phase = "linear"

        return dict(
            from_phase=from_phase,
            to_phase=to_phase,
        )


class FinalGameResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        total = sum(p.gross_profit for p in self.in_all_rounds())
        return dict(player_accumulated_payoff=total)


page_sequence = [
    GroupFormationWaitPage,
    Contribution,
    GroupWaitPage,
    ObservationPage,
    SecondGame,
    FinalGameResults,
]