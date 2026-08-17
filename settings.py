from os import environ

SESSION_CONFIGS = [


# Test
    dict(
        name="test",
        display_name="test 21-18-3",
        num_demo_participants=21, #space for 21 (signed-up) participants; the first 18 will continue to the games
        public_goods_first="linear",
        composition_first="homogeneous",
        use_browser_bots=False,
        app_sequence=[
            "intro_pnb",
            "selection",
            "public_goods_game_1",
            "public_goods_game_2",
            "reward",
        ],

        completionlink_included=(
            "https://app.prolific.com/"
            "submissions/complete?cc=INCLUDED"
        ),

        completionlink_excluded=(
                    "https://app.prolific.com/"
                    "submissions/complete?cc=EXCLUDED"
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
            "selection",
            "public_goods_game_1",
            "public_goods_game_2",
            "reward",
        ],
        completionlink_included=(
            "https://app.prolific.com/"
            "submissions/complete?cc=INCLUDED"
        ),

        completionlink_excluded=(
            "https://app.prolific.com/"
            "submissions/complete?cc=EXCLUDED"
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
            "selection",
            "public_goods_game_1",
            "public_goods_game_2",
            "reward",
        ],
        completionlink_included=(
            "https://app.prolific.com/"
            "submissions/complete?cc=INCLUDED"
        ),

        completionlink_excluded=(
            "https://app.prolific.com/"
            "submissions/complete?cc=EXCLUDED"
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
            "selection",
            "public_goods_game_1",
            "public_goods_game_2",
            "reward",
        ],
        completionlink_included=(
            "https://app.prolific.com/"
            "submissions/complete?cc=INCLUDED"
        ),

        completionlink_excluded=(
            "https://app.prolific.com/"
            "submissions/complete?cc=EXCLUDED"
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
            "selection",
            "public_goods_game_1",
            "public_goods_game_2",
            "reward",
        ],
        completionlink_included=(
            "https://app.prolific.com/"
            "submissions/complete?cc=INCLUDED"
        ),

        completionlink_excluded=(
            "https://app.prolific.com/"
            "submissions/complete?cc=EXCLUDED"
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

contribution_time = 90 #time out for contribution
observation_time = 60 #time out for observation
introduction_time = 300 #time out for instruction of production function after being grouped


#configure a room
ROOMS = [
    dict(
        name='public_goods_game',
        display_name='Public Goods Game'
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.10, participation_fee=2.00, doc=""
)

PARTICIPANT_FIELDS = ['consent']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '3570031017708'
