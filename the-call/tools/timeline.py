"""Single source of truth for "The Call" timing. build.py and make_placeholders.py read this.

Each line: id, who, start, dur, media_start (trim into assets/footage/<id>.mp4), layout, caption.
layouts: full (anchor fills the frame), pip (anchor in a corner box over graphics),
         top / bottom (split screen halves), voice (audio only, picture hidden).
Times sit on the 150 BPM grid (0.4 s beat) of assets/music/call-bed.mp3.
"""

LENGTH = 30.4

LINES = [
    # id    who       start  dur  media_start layout   caption (English, burned in)
    ("A1", "aditya", 0.0, 2.0, 0.0, "full", "DELHI, AN IMPORTANT ANNOUNCEMENT."),
    ("V1", "vinol", 2.0, 2.0, 0.0, "full", "YOUR SOFA CAREER ENDS TODAY."),
    ("A2", "aditya", 4.0, 1.2, 0.0, "full", "BECAUSE DELHI NOW HAS…"),
    ("V2", "vinol", 5.2, 1.2, 0.0, "full", ""),
    ("A3", "aditya", 6.4, 1.2, 0.0, "pip", ""),
    ("V3", "vinol", 7.6, 1.2, 0.0, "pip", ""),
    ("A4", "aditya", 8.8, 1.2, 0.0, "pip", ""),
    ("V4", "vinol", 10.0, 1.2, 0.0, "pip", ""),
    ("A5", "aditya", 11.2, 1.2, 0.0, "pip", ""),
    ("V5", "vinol", 12.4, 1.2, 0.0, "pip", ""),
    ("A6", "aditya", 13.6, 1.2, 0.0, "pip", ""),
    ("V6", "vinol", 14.8, 1.6, 0.0, "pip", ""),
    ("A7", "aditya", 16.4, 1.2, 0.0, "pip", ""),
    ("V7", "vinol", 17.6, 1.2, 0.0, "pip", ""),
    ("A8", "aditya", 18.8, 2.0, 0.0, "pip", ""),
    ("V8", "vinol", 20.8, 2.0, 0.0, "full", "SO TELL MUM…"),
    ("A9", "aditya", 22.8, 2.0, 0.0, "full", "…YOU'LL BE LATE FOR DINNER TONIGHT."),
    ("V9", "vinol", 24.8, 1.2, 0.0, "full", ""),
    ("A10", "aditya", 26.0, 1.2, 0.0, "full", ""),
    ("A11", "aditya", 27.2, 1.2, 0.0, "top", ""),
    ("V10", "vinol", 27.2, 1.2, 0.0, "bottom", ""),
]

# audio of the unison line keeps playing over the logo end card
TAIL = {"A11": 2.4, "V10": 2.4}

GAMES = [
    # line, plate, title lines, tag
    ("A3", "01", ["EA SPORTS", "FC"], "FOOTBALL · 1V1 / CO-OP"),
    ("V3", "03", ["VALORANT"], "TACTICAL FPS · 5V5"),
    ("A4", "04", ["COUNTER-", "STRIKE 2"], "TACTICAL FPS · 5V5"),
    ("V4", "05", ["ROCKET", "LEAGUE"], "CAR FOOTBALL · 3V3"),
    ("A5", "06", ["BGMI"], "BATTLE ROYALE · SQUADS"),
    ("V5", "07", ["CALL OF", "DUTY"], "FPS · SQUADS"),
    ("A6", "08", ["TEKKEN 8"], "FIGHTING · 1V1"),
]

NAMES = {"aditya": ("ADITYA SONI", "ON LOCATION"), "vinol": ("VINOL ARUN", "NXT STUDIO")}
