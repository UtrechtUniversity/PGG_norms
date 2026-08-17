from otree.api import *


doc = """
show the participants points and earnings
Redirect to Prolific
"""


class Constants(BaseConstants):
    name_in_url = 'reward'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    pass


# PAGES
class PaymentInfo(Page):

    @staticmethod
    def vars_for_template(player):
        participant = player.participant
        session = player.subsession.session

        payable_points = participant.payoff

        points_value = (
            payable_points.to_real_world_currency(
                session
            )
        )

        base_payment = session.config[
            "participation_fee"
        ]

        total_payment = max(
            points_value,
            base_payment,
        )

        bonus_payment = (
            total_payment
            - base_payment
        )

        return dict(
            payable_points=payable_points,
            conversion_per_point=(
                cu(1).to_real_world_currency(
                    session
                )
            ),
            base_payment=base_payment,
            bonus_payment=bonus_payment,
            total_payment=total_payment,
            completionlink=session.config[
                "completionlink_included"
            ],
        )

page_sequence = [PaymentInfo]

