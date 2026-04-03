from os import environ

SESSION_CONFIGS = [
    dict(
        name="public_goods_game1",
        display_name="PNB homogeneous",
        condition="homogeneous",
        num_demo_participants=6,
        app_sequence=["consent", "intro_pnb", "public_goods_game", "reward"],
        completionlink='https://app.prolific.com/submissions/complete?cc=TEST'
    ),

    dict(
        name="public_goods_game2",
        display_name="PNB heterogeneous",
        condition="heterogeneous",
        num_demo_participants=6,
        app_sequence=["consent", "intro_pnb", "public_goods_game", "reward"],
        completionlink='https://app.prolific.com/submissions/complete?cc=TEST'
    )
]

# set some central parameters to be used across apps:
players_per_group = 3
efficiency_factor = 0.7
num_rounds = 3

#configure a room
ROOMS = [
    dict(
        name='public_goods_game',
        display_name='Public Goods Game'
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['consent']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '3570031017708'
