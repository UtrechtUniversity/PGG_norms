from otree.api import *


doc = """
introduction
personal normative beliefs
"""

from settings import (
    players_per_group as ppp,
    efficiency_factor as ef,
    num_rounds as nr
)

class C(BaseConstants):
    NAME_IN_URL = 'intro_pnb'
    title = "Public goods game"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    endowment = 20
    efficiency_factor = ef


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    pnb = models.CurrencyField(
        min=0,
        max=C.endowment,
        initial=None,
        verbose_name="According to you, what is the appropriate amount that each member should contribute to the group account?",
        # Specify to use a slider widget
        widget=widgets.RadioSelect,
        choices=[i for i in range(0, C.endowment + 1)],
    )

    prolific_id = models.StringField(default="")

    arrived_waitpage = models.BooleanField(initial=False)



# PAGES
class IntroductionPage(Page):
    def before_next_page(player, timeout_happened):
        # read in Prolific ID
        participant_label = player.participant.label
        player.prolific_id = participant_label


class PNB(Page):
    form_model = 'player'
    form_fields = ['pnb']

    def vars_for_template(player):
        return {
            'endowment': C.endowment,
            'efficiency_factor': C.efficiency_factor,
            'players_per_group': ppp,
        }

    def error_message(player, values):
        if values.get('pnb') is None:
            return "Please indicate what you think is the appropriate contribution."

    def before_next_page(player, timeout_happened):
        player.participant.vars['pnb'] = player.pnb


class ResultsWaitPage(WaitPage):
    template_name = 'intro_pnb/ResultsWaitPage.html'

    @staticmethod
    def is_displayed(player: Player):
        return True

    def vars_for_template(player):
        if not player.arrived_waitpage:
            player.arrived_waitpage = True

        # get all players in the subsession
        waiting_players = player.subsession.get_players()

        total_arrived = sum(bool(p.arrived_waitpage) for p in waiting_players)

        # determine group size and how many are needed
        group_size = ppp
        total_needed = group_size

        if total_needed == 0:
            percent = 0
        else:
            percent = (total_arrived / total_needed) * 100
            percent = min(int(percent), 99)

        return dict(
            percent=percent,
        )

    @staticmethod
    def after_all_players_arrive(group):
        pass

page_sequence = [
    IntroductionPage,
 PNB, ResultsWaitPage]
