from enum import Enum

class SnakeState(Enum):
    HUNGRY = 'hungry' #hungry and superior
    #SATURATED = 'saturated'
    SUPERIOR = 'superior' #superior and not hungry
    INFERIOR = 'inferior' #inferior and not hungry
    INFERIORHUNGRY = 'inferiorhungry' #inferior and hungry