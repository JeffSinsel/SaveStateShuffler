# Options

# Platform
# Only 1 of these 2 can be True at a time
PLATFORM_N64 = False # Set to True if using project 64 for game, otherwise set to False
PLATFORM_GCN = False # Set to True if using dolphin for game, otherwise set to False

# Emulator Keybinds
# Make sure your keybinds are the same here and in the emulator
N64_SAVE_STATE = "F5" # Default save state button in Project 64, stored as string of key 
N64_LOAD_STATE = "F7" # Default load state button in Project 64, stored as string of key
N64_PAUSE = "F2" # Default pause key in Project 64, stored as string of key
GCN_PAUSE = "F11" # Default pause key in Dolphin, stored as string of key

# Basic Default Settings
FINISH_SAVE_BUTTON = "space" # Button you press to finish a save, as a string
PAUSE_BUTTON = "p" # Button you press to pause the shuffler, as a string
MINIMUN_SLOT_TIME = 5 # Minimum time you play in a save slot, recommend this stays >=1
MAXIMUM_SLOT_TIME = 20 # Maximum time you play in a save slot, recommend this stays >1
COUNTDOWN = 3 # Countdown after htting spacebar to begin, in seconds

# Optional Features
TIMER = True # Set to True for timer that will return time when all saves are completed, otherwise set to False
SEED = None # Set to the same integer (ex. 102139) as your friends if you want to play on fair ground, or if you want the same randomness each time 

# TTS Finetuning
VOICE_TEXT_FINISH_SAVE = "Save Completed" # Text said after every save is removed, as a string
VOICE_TEXT_LAST_SAVE = "Final Save!" # Text said when on last save, as a string
VOICE_TEXT_DONE = "Game Completed, Pog!" # Text said when no saves are left, as a string

# OBS Settings
USING_OBS_WEBSOCKETS = False # Set to True for the number of remaining games to be output to obs, otherwise set to False
OBS_TEXT_SOURCE = "SAVES LEFT" # Name this the same as your text element you want to update in OBS, as a string
OBS_TEXT_DISPLAY = "SAVES LEFT: " # The text to be displayed in OBS, this will have the number of slots left at the end, as a string
OBS_HOST = "localhost" # Hostname to connect to (Default is "localhost")
OBS_PORT = 4455 # TCP Port to connect to (Default is 4455)
OBS_PASSWORD = "" # Password for the websocket server (Leave this field empty if auth is not enabled)
# For troubleshooting OBS checkout https://github.com/obsproject/obs-websocket

# Advanced Default Settings
KEY_COOLDOWN = 1 # Cooldown time in between key presses, in seconds, recommend this stays >=1
remaining_slots = ['1','2','3','4','5','6','7','8','9','0'] # Starting slots, if you need to start halfway through or would like less save to start, then edit the list appropriately 