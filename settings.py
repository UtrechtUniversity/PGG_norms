from os import environ

SESSION_CONFIGS = [


# Test
    dict(
        name="test",
        display_name="test 21-18-3",
        num_demo_participants=21,
        public_goods_first="linear",
        composition_first="homogeneous",
        use_browser_bots=True,
        app_sequence=[
            "intro_pnb",
            "selection",
            "public_goods_game_1",
            "public_goods_game_2",
            "reward",
        ],
        completionlink=(
            "https://app.prolific.com/"
            "submissions/complete?cc=TEST"
        ),
    ),

    # Arm A:
    # Linear → stepwise
    # Homogeneous → heterogeneous
    dict(
        name="pgg_linear_homogeneous_first",
        display_name="Linear first – homogeneous first",
        num_demo_participants=90,
        public_goods_first="linear",
        composition_first="homogeneous",
        use_browser_bots=False,
        app_sequence=[
            "intro_pnb",
            "public_goods_game_1",
            "public_goods_game_2",
            "reward",
        ],
        completionlink=(
            "https://app.prolific.com/"
            "submissions/complete?cc=TEST"
        ),
    ),

    # Arm B:
    # Linear → stepwise
    # Heterogeneous → homogeneous
    dict(
        name="pgg_linear_heterogeneous_first",
        display_name="Linear first – heterogeneous first",
        num_demo_participants=90,
        public_goods_first="linear",
        composition_first="heterogeneous",
        use_browser_bots=False,
        app_sequence=[
            "intro_pnb",
            "public_goods_game_1",
            "public_goods_game_2",
            "reward",
        ],
        completionlink=(
            "https://app.prolific.com/"
            "submissions/complete?cc=TEST"
        ),
    ),

    # Arm C:
    # Stepwise → linear
    # Homogeneous → heterogeneous
    dict(
        name="pgg_stepwise_homogeneous_first",
        display_name="Stepwise first – homogeneous first",
        num_demo_participants=90,
        public_goods_first="stepwise",
        composition_first="homogeneous",
        use_browser_bots=False,
        app_sequence=[
            "intro_pnb",
            "public_goods_game_1",
            "public_goods_game_2",
            "reward",
        ],
        completionlink=(
            "https://app.prolific.com/"
            "submissions/complete?cc=TEST"
        ),
    ),

    # Arm D:
    # Stepwise → linear
    # Heterogeneous → homogeneous
    dict(
        name="pgg_stepwise_heterogeneous_first",
        display_name="Stepwise first – heterogeneous first",
        num_demo_participants=90,
        public_goods_first="stepwise",
        composition_first="heterogeneous",
        use_browser_bots=False,
        app_sequence=[
            "intro_pnb",
            "public_goods_game_1",
            "public_goods_game_2",
            "reward",
        ],
        completionlink=(
            "https://app.prolific.com/"
            "submissions/complete?cc=TEST"
        ),
    ),
]
# set some central parameters to be used across apps:

number_of_players = 18
players_per_group = 3
num_rounds = 2

endowment = 20
group_multiplier = 1.5
threshold_per_player = 10

# Linear PGG
efficiency_factor = group_multiplier / players_per_group

# Threshold PGG
threshold = threshold_per_player * players_per_group
reward = efficiency_factor * threshold










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
