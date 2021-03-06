# TODO: Train Parameters with genetic algorithm


class Params_Decision:

    MONITOR_TIME = 0.150
    REDUCED_MONITORING_TIME = 100
    UPDATE_FREQUENCY = 5
    CLOSEST_HEAD_BOUNDARY = 5
    BOARD_11 = 0
    BOARD_15 = 0
    BOARD_18 = 0


class Params_Automat:

    HEAD_DIST_AVG_AGGRESSIVE = 4
    HEAD_DIST_AVG_HUNGRY = 5
    ENEMY_HEALTH_BOUNDARY = 20
    MONITOR_LENGTH = 20
    MONITOR_DISTANCE = 10
    MONITOR_FOOD = 20
    PATH_LENGTH = 10

    HUNGER_HEALTH_BOUNDARY = 30
    ROUND_NUMBER_BOUNDARY = 150
    ENEMIES_ALIVE = 3


class Params_MovementProfile:

    FOOD_PROFILE_DIST_BOUNDARY = 10
    HEAD_PROFILE_DIST_BOUNDARY = 15


class Params_Anxious:

    ALPHA_DISTANCE_ENEMY_HEAD = [5, 3, 1]
    BETA_DISTANCE_CORNERS = [5, 1, 0]
    GAMMA_DISTANCE_FOOD = [5, 7, 2]
    EPSILON_NO_BORDER = [10, 5, 5]
    THETA_DISTANCE_MID = [1, 1, 0]

    OMEGA_FLOOD_FILL_MAX = [0, 0, 0]
    OMEGA_FLOOD_FILL_MIN = [10, 10, 10]
    OMEGA_FLOOD_DEAD = [3, 7, 10]
    RHO_ESCAPE_CORRIDOR = [7, 3, 1]
    TAU_PATH_LENGTH = [1, 1, 0]


class Params_Aggressive:
    KILL_PATH = []


class Params_ActionPlan:

    SNAKE_RADIUS = 5


class Params_ValidActions:

    DEPTH = 15
    DIST_TO_ENEMY = 15
    BODY_VALUE = 10
    HEAD_VALUE = 50
    AREA_VALUE = 5
    FOOD_BOUNDARY = 30


class Params_Fitness:
    board = None
    turn = 0
    my_id = ""
