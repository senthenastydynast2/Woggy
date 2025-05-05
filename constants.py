import os
import math

LETTER_PROBABILITIES_ENGLISH = {
    'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12,
    'F': 2, 'G': 3, 'H': 2, 'I': 9, 'J': 1,
    'K': 1, 'L': 4, 'M': 2, 'N': 6, 'O': 8,
    'P': 2, 'Q': 1, 'R': 6, 'S': 6, 'T': 6,
    'U': 4, 'V': 2, 'W': 2, 'X': 1, 'Y': 2,
    'Z': 1
}
LETTER_VALUES_ENGLISH = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1,
    'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8,
    'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1,
    'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1,
    'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4,
    'Z': 10
}

LETTER_PROBABILITIES_SPANISH = {
    'A': 12, 'B': 2, 'C': 4, 'CH': 1, 'D': 5,
    'E': 12, 'F': 1, 'G': 4,  'H': 2, 'I': 6,
    'J': 1, 'L': 4, 'LL': 1, 'M': 2, 'N': 5,
    'Ñ': 1, 'O': 9, 'P': 2, 'QU': 1, 'R': 5,
    'RR': 1, 'S': 6, 'T': 4, 'U': 5, 'V': 1,
    'X': 1, 'Y': 1, 'Z': 1
}

LETTER_VALUES_SPANISH = {
    'A': 1, 'B': 3, 'C': 3, 'CH': 5, 'D': 2,
    'E': 1, 'F': 4, 'G': 2,  'H': 4, 'I': 1,
    'J': 8, 'L': 1, 'LL': 8, 'M': 3, 'N': 1,
    'Ñ': 8, 'O': 1, 'P': 3, 'QU': 5, 'R': 1,
    'RR': 8, 'S': 1, 'T': 1, 'U': 1, 'V': 4,
    'X': 8, 'Y': 5, 'Z': 10
}


LENGTH_MULTIPLIERS = {
    3: 1,
    4: 1.25,
    5: 1.75,
    6: 2.5,
    7: 3,
    8: 3.5,
    9: 4,
    10: 5,
    11: 6,
    12: 7,
    13: 8,
    14: 9,
    15: 10,
    16: 12
}
DICTIONARY_FILE_ENGLISH = os.path.join("Dictionaries", "OTCWL69.txt")
DICTIONARY_FILE_SPANISH = os.path.join("Dictionaries", "Spanish.txt")
DICTIONARY_FILE = DICTIONARY_FILE_ENGLISH
TILES_FOLDER_ENGLISH = os.path.join("Tiles", "English")
TILES_FOLDER_SPANISH = os.path.join("Tiles", "Spanish")
TILES_FOLDER = TILES_FOLDER_ENGLISH
BADGES_FOLDER = os.path.join("Tiles", "Badges")
SETTINGS_FOLDER = "Settings"
SETTINGS_FOLDER = "Settings"
SETTINGS_FILE   = os.path.join(SETTINGS_FOLDER, "settings.json")
SCRAPING_DOG_URL = "https://api.scrapingdog.com/google_images/" #For WTF function only - optional!

# round timers per board potential
TIMER_MAP = {
    1: 11,   
    2: 13,   
    3: 14,  
    4: 16,   
    5: 17,  
    6: 18,  #Impo
    
    7: 20,  
    8: 22,  
    9: 24,  #Desert
    
    10: 33, 
    11: 36, 
    12: 39, #Closed
    
    13: 45,
    14: 50, #Dry
    
    15: 70,
    16: 85,
    17: 100, #Boring
    
    18: 110,
    19: 120, #Average
    
    20: 130,
    21: 140, #Decent
    
    22: 155,
    23: 165, #Open
    
    24: 175, #Juicy
    
    25: 185,
    26: 195, #Insane
    
    27: 210,
    28: 240, #Moshpit
    
    29: 220,
    30: 230,
    31: 245,
    32: 260 #Godlike
}

BOARD_HANDICAP_MAP = {
    1: -24.5,
    2: -24.5,   #Desertic Board
    3: -22,  
    4: -20,   
    5: -18,
    6: -17,
    7: -16,
    8: -15,
    9: -14,
    10: -13,
    11: -12,
    12: -10,   
    21: 5,    
    22: 5,
    23: 6,
    24: 7,
    25: 8,
    26: 11,
    27: 14,
    28: 17,
    29: 20,
    30: 23,
    31: 26,
    32: 30
}

# Background colors by board potential, please fix
BOARD_BG_COLORS = {
    1: 'red',
    2: 'firebrick',
    3: 'firebrick',
    4: 'firebrick',
    5: 'firebrick',
    6: 'firebrick',
    7: 'firebrick',
    8: 'firebrick',
    9: 'firebrick',
    10: 'lightcoral',
    11: 'lightcoral',
    12: 'lightcoral',
    13: 'lightcoral',
    14: 'silver',
    15: 'silver',
    16: 'silver',
    17: 'silver',
    18: 'wheat',
    19: 'wheat',
    20: 'wheat',
    21: 'wheat',
    22: 'mediumaquamarine',
    23: 'mediumaquamarine',
    24: 'mediumaquamarine',
    25: 'lightskyblue',
    26: 'lightskyblue',
    27: 'lightskyblue',
    28: 'royalblue',
    29: 'royalblue',
    30: 'mediumorchid',
    31: 'mediumorchid',
    32: 'indigo'
}


# classification thresholds: (max_possible_score, label, color, board_value)
CLASSIFICATION_THRESHOLDS = [
    (700,          "Impossible Board!",    "red",                1),    
    (800,          "Desertic Board",       "firebrick",          2),
    (900,          "Desertic Board",       "firebrick",          3),
    (1000,         "Desertic Board",       "firebrick",          4),  
    (1100,         "Closed Board",         "tomato",             5),
    (1250,         "Closed Board",         "tomato",             6), #Impossible
    
    
    
    (1500,         "Closed Board",         "tomato",             7), 
    (1750,         "Closed Board",         "lightcoral",         8),
    (2000,         "Closed Board",         "lightcoral",         9), #Desertic
    
    
    
    (2250,         "Dry Board",            "lightcoral",         10),
    (2500,         "Dry Board",            "lightcoral",         11),
    (3000,         "Dry Board",            "lightcoral",         12), #Closed
    
    
    (4000,         "Dry Board",            "lightcoral",         13),   
    (5000,         "Lackluster Board",     "silver",             14), #Dry Board
    
    (6000,         "Lackluster Board",     "silver",             15),
    (7000,         "Lackluster Board",     "silver",             16),   
    (8000,         "Average Board",        "silver",             17), #Boring
    
    
    (9000,         "Average Board",        "wheat",              18),          
    (10000,        "Average Board",        "wheat",              19), #Average
    
    (11000,        "Average Board",        "wheat",              20),
    (13500,        "Average Board",        "wheat",              21), #Decent
    
    (16000,        "Average Board",        "mediumaquamarine",   22),   
    (18500,        "Open Board",           "mediumaquamarine",   23), #Open
    
    (21000,        "Open Board",           "mediumaquamarine",   24), #Juicy
    
    (23500,        "Open Board",           "lightskyblue",       25),  
    (26000,        "Juicy Board",          "lightskyblue",       26), #Insane
    
    (28500,        "Juicy Board",          "lightskyblue",       27),
    (31000,        "Juicy Board",          "royalblue",          28), #Moshpit
    
    (33500,        "Insane Board",         "royalblue",          29), #Godlike
    (36000,        "Insane Board",         "mediumorchid",       30),
    (38500,        "Insane Board",         "mediumorchid",       31),  
    (float('inf'), "Godlike Board!",       "indigo",             32)
]



RANK_THRESHOLDS = [
    (0.050, ('F-',
    'firebrick', "It isn't humanly possible to score this low, so I'm just going to assume your keyboard broke at the beginning of the round. | F-")),
    (0.075, ('F',
    'firebrick', "Wake up! That performance was abysmal! Absolute fail! | F")),
    (0.100, ('F+',
    'firebrick', "Time to hit the gym, porkchop. The dictionary gym, that is. Too many missed opportunities to count! | F+")),
    (0.125, ('D-',
    'darkgoldenrod', "Lots of room for improvement, and I mean lots. Work on that speed and that vocab! D-")),
    (0.150, ('D',
    'darkgoldenrod', "We all have our bad rounds. Not every round has easy to spot words - practice those tricky words to move out of ruts like these! | D")),
    (0.175, ('D+',
    'darkgoldenrod', "Faster, faster, faster is the name of the game if you want to avoid getting scores like these! | D+")),
    (0.200, ('C-',
    'lemonchiffon', "Marginal performance. Keep practicing! | C-")),
    (0.225, ('C',
    'lemonchiffon', "Not bad! Keep pushing higher! | C")),
    (0.275, ('C+',
    'lemonchiffon', "Nice! Slightly above average. Keep at it! | C+")),
    (0.325, ('B-',
    'steelblue', "Good job! Perhaps a missed opportunity here and there, but a great job regardless. | B-")),
    (0.365, ('B',
    'steelblue', "Pretty damn good if I do say so myself! Somebody's been practicing! | B")),
    (0.440, ('B+',
    'steelblue', "Rising through the scoreboards, leaving competition in the dust... it's the mighty Woggy challenger tearing through the ranks! Great job! | B+")),
    (0.495, ('A-',
    'dodgerblue', "Who's a smartie? You're a smartie! And as someone like you probably knows, smartie is a great Scrabble word too! Welcome to true winners' territory! | A-")),
    (0.545, ('A',
    'dodgerblue', "Outstanding! That keyboard of yours must be smoking right now! Flaunt your rank loud and proud, champ! | A")),
    (0.625, ('A+',
    'dodgerblue', "Incredible!! Playing like an absolute pro! It's not every day I see scores like this. Sheer talent! | A+")),
    (0.675, ('S',
    'cyan', "RED ALERT! We have an overachiever in the house! Getting here is a result of a keen eye and optimal play... and a little luck. Welcome to elite territory, my friend! | S")),
    (0.755, ('S+',
    'cyan', "Yup -- you already know it: You spotted all the good words, nailed a lot of words in general, and probably got none of them wrong. Here's a badge for a flawless performance. Huzzah! | S+")),
    (1.00, ('SS',
    'blueviolet', "Alright smartypants, good job... on getting your cheats to work. Only a bot can get this rank or else I'm not balancing the game properly! Or... you are simply a god. A Woggy God. That's your rank. | SS"))
]


def get_rank_from_ratio(rs: float) -> str:
    """Return the rank string for a given ratio."""
    for threshold, rank in RANK_THRESHOLDS:
        if rs <= threshold:
            return rank
    return 'S++'
    
def get_rank_info(rs: float) -> tuple[str,str,str]:
    """Clamp rs to 1.0, round up to the nearest 0.001, then return (rank, color, message)."""
    rs = min(rs, 1.0)
    rs = math.ceil(rs * 1000) / 1000.0
    for thr, info in RANK_THRESHOLDS:
        if rs <= thr:
            return info
    return RANK_THRESHOLDS[-1][1]

#Number of words required to get the badge, subjective for each board type
WORD_HOGGER_THRESHOLDS = {
    1: 3,
    2: 4,
    3: 5,
    4: 5,
    5: 6,
    6: 6, #Impo
    7: 7,
    8: 8,
    9: 9, #Desert   
    10: 10,
    11: 11,
    12: 12, #Closed  
    13: 13,
    14: 15, #Dry
    15: 19,
    16: 22,
    17: 25, #Boring
    18: 33,
    19: 36, #Average
    20: 39,
    21: 45, #Decent
    22: 48,
    23: 51, #Open
    24: 54, #Juicy
    25: 57,
    26: 60, #Insane  
    27: 70,
    28: 80, #Moshpit 
    29: 85,
    30: 90,
    31: 95,
    32: 100 #Godlike
}

def get_wordhogger_threshold(bpv: int) -> int:
    return WORD_HOGGER_THRESHOLDS.get(bpv, 0)