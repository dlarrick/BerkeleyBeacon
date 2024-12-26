import enum

# 2 == LR Middle; 6 == actual Beacon
# BEACON = 2
BEACON = 10

RUN_TIMES = [['sunset', '23:15'], ['5:45', 'sunrise']]
# debug/test:
# RUN_TIMES = [['sunset', '23:00'], ['6:00', '23:00']]

SLEEP_DURATION = 2.5

class Color(enum.Enum):
    BLACK = 0
    BERKELEY_BLUE = 1  # like the real beacon
    BERKELEY_RED = 2
    WHITE = enum.auto()
    RED = enum.auto()
    ORANGE = enum.auto()
    YELLOW = enum.auto()
    GREEN = enum.auto()
    KELLY_GREEN = enum.auto()
    BLUE = enum.auto()
    INDIGO = enum.auto()
    VIOLET = enum.auto()
    PINK = enum.auto()

COLORVALS = {
    Color.BLACK: [0, 0],
    Color.WHITE: [0.304, 0.3206],
    Color.BERKELEY_BLUE: [0.1947, 0.2229],
    Color.BERKELEY_RED: [0.6663, 0.2978],
    Color.RED: [0.675, 0.322],
    Color.ORANGE: [0.5707, 0.3989],
    Color.YELLOW: [0.4777, 0.4673],
    Color.GREEN: [0.409, 0.518],
    Color.KELLY_GREEN: [0.409, 0.518],
    Color.BLUE: [0.1548, 0.1116],
    Color.INDIGO: [0.1837, 0.0624],
    Color.VIOLET: [0.2363, 0.0878],
    Color.PINK: [0.3442, 0.1779]
}

SEQUENCES = {
    "off": [Color.BLACK],
    "clear": [Color.BERKELEY_BLUE],
    "clouds": [Color.BERKELEY_BLUE, Color.BLACK],
    "rain": [Color.BERKELEY_RED],
    "snow": [Color.BERKELEY_RED, Color.BLACK],
    "severe": [Color.ORANGE, Color.BLACK],
    "error": [Color.RED, Color.VIOLET],
    "white": [Color.WHITE],
    "black": [Color.BLACK],
    "red": [Color.RED],
    "orange": [Color.ORANGE],
    "yellow": [Color.YELLOW],
    "green": [Color.GREEN],
    "kelly_green": [Color.KELLY_GREEN],
    "blue": [Color.BLUE],
    "indigo": [Color.INDIGO],
    "violet": [Color.VIOLET],
    "pink": [Color.PINK],
    "fl_blue": [Color.BLACK, Color.BERKELEY_BLUE],
    "fl_red": [Color.BLACK, Color.BERKELEY_RED],
    "christmas": [Color.RED, Color.GREEN],
    "rainbow": [Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN,
                Color.BLUE, Color.INDIGO, Color.VIOLET],
    "valentine": [Color.RED, Color.PINK],
    "flag": [Color.RED, Color.WHITE, Color.BLUE],
    "juneteenth": [Color.RED, Color.GREEN, Color.BLACK],
    "halloween": [Color.ORANGE, Color.BLACK, Color.INDIGO],
    "indigenous": [Color.ORANGE, Color.YELLOW, Color.RED, Color.WHITE],
}

HOLIDAYS = {
    "New Year's Day": "rainbow",
    'Memorial Day': "flag",
    'Juneteenth National Independence Day': "juneteenth",
    'Independence Day': "flag",
    'Labor Day': "flag",
    'Veterans Day': None,
    'Thanksgiving': None,
    'Christmas Day': "christmas",
    "Valentine's Day": "valentine",
    "Evacuation Day; Saint Patrick's Day": "kelly_green",
    'Halloween': "halloween",
    'Groundhog Day': None,
    'Martin Luther King Jr. Day': "juneteenth",
    "Washington's Birthday": "flag",
    'Columbus Day': "indigenous",
    "Patriots' Day": "flag",
}
# Would be nice to add Earth Day
