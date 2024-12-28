import os
import enum

# 2 == LR Middle; 10 == actual Beacon
BEACON = int(os.getenv("BEACON", "10"))

RUN_TIMES = ([['sunset', '23:00'], ['6:00', '23:00']] if os.getenv("BEACON")
             else [['sunset', '23:15'], ['5:45', 'sunrise']])
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
    CHARTREUSE = enum.auto()
    YELLOW_GREEN = enum.auto()
    BLUE_GREEN = enum.auto()
    BLUEGRASS = enum.auto()
    BLUE = enum.auto()
    PALE_BLUE = enum.auto()
    INDIGO = enum.auto()
    VIOLET = enum.auto()
    PINK = enum.auto()
    PALE_PINK = enum.auto()

COLORVALS = {
    Color.BLACK: [0, 0],
    Color.WHITE: [0.304, 0.3206],
    Color.BERKELEY_BLUE: [0.1947, 0.2229],
    Color.BERKELEY_RED: [0.6663, 0.2978],
    Color.RED: [0.675, 0.322],
    Color.ORANGE: [0.5707, 0.3989],
    Color.YELLOW: [0.4777, 0.4673],
    Color.GREEN: [0.409, 0.518],
    Color.KELLY_GREEN: [0.1679, 0.618],
    Color.CHARTREUSE: [0.4418, 0.4958],
    Color.YELLOW_GREEN: [0.3789, 0.5431],
    Color.BLUE_GREEN: [0.3872, 0.4749],
    Color.BLUEGRASS: [0.2808, 0.2648],
    Color.BLUE: [0.1548, 0.1116],
    Color.INDIGO: [0.1837, 0.0624],
    Color.VIOLET: [0.2363, 0.0878],
    Color.PINK: [0.3442, 0.1779],
    Color.PALE_PINK: [0.3442, 0.1779],
    Color.PALE_BLUE: [0.2941, 0.2064],
}

SEQUENCES = {
    "white": [Color.WHITE],
    "black": [Color.BLACK],
    "red": [Color.RED],
    "orange": [Color.ORANGE],
    "yellow": [Color.YELLOW],
    "green": [Color.GREEN],
    "blue": [Color.BLUE],
    "indigo": [Color.INDIGO],
    "violet": [Color.VIOLET],
    "pink": [Color.PINK],

    "off": [Color.BLACK],
    "clear": [Color.BERKELEY_BLUE],
    "clouds": [Color.BERKELEY_BLUE, Color.BLACK],
    "rain": [Color.BERKELEY_RED],
    "snow": [Color.BERKELEY_RED, Color.BLACK],
    "severe": [Color.ORANGE, Color.BLACK],
    "error": [Color.RED, Color.VIOLET],

    "blue_white": [Color.BLUE, Color.WHITE],
    "christmas": [Color.RED, Color.GREEN],
    "easter": [Color.PALE_PINK, Color.PALE_BLUE],
    "flag": [Color.RED, Color.WHITE, Color.BLUE],
    "greens": [Color.GREEN, Color.BLUEGRASS, Color.YELLOW_GREEN, Color.BLUE_GREEN,
               Color.KELLY_GREEN, Color.CHARTREUSE],
    "halloween": [Color.ORANGE, Color.BLACK, Color.INDIGO],
    "indigenous": [Color.ORANGE, Color.YELLOW, Color.RED, Color.WHITE],
    "juneteenth": [Color.RED, Color.GREEN, Color.BLACK],
    "kelly_green": [Color.KELLY_GREEN],
    "purples": [Color.INDIGO, Color.VIOLET],
    "rgb": [Color.RED, Color.GREEN, Color.BLUE],
    "rainbow": [Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.BLUEGRASS, Color.BLUE,
                Color.INDIGO, Color.VIOLET],
    "valentine": [Color.RED, Color.PINK],
}

MORE_HOLIDAYS = [
    ("apr_22", "Earth Day"),
    ("easter_sunday", "Easter"),
    ("apr_21", "Lis's Birthday"),
    ("sep_18", "Doug's Birthday"),
    ("dec_26", "Test"),
    ("dec_31": "New Year's Eve"),
]

HOLIDAYS = {
    "Doug's Birthday": "rgb",
    "Earth Day": "greens",
    "Easter": "easter",
    "Evacuation Day; Saint Patrick's Day": "kelly_green",
    "Lis's Birthday": "purples",
    "New Year's Day": "blue_white",
    "New Year's Eve": "rainbow",
    "Patriots' Day": "flag",
    "Valentine's Day": "valentine",
    "Washington's Birthday": "flag",
    'Christmas Day': "christmas",
    'Columbus Day': "indigenous",
    'Groundhog Day': None,
    'Halloween': "halloween",
    'Independence Day': "flag",
    'Juneteenth National Independence Day': "juneteenth",
    'Labor Day': "flag",
    'Martin Luther King Jr. Day': "juneteenth",
    'Memorial Day': "flag",
    'Test': None,
    'Thanksgiving': None,
    'Veterans Day': None,
}
