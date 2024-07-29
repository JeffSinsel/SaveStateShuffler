# Game Shuffler
# Modified and Added to by Jeff Sinsel, Inspired and Originally Written by DouglasDouglas

print("Loading...") # Gives TTS time to build and on exe lets user know that the python has started

# Import libraries
import random
import time
import keyboard
import sys
import os
import shutil
import threading
from rich import print
from gtts import gTTS
from playsound import playsound
from importlib.machinery import SourceFileLoader
import obsws_python as obs

# Makes sure paths line up on script vs exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable) # EXE version of path
elif __file__:
    application_path = os.path.dirname(__file__) # Script version of path

config = SourceFileLoader("",(application_path+"/config.py")).load_module() # Pull from the config file, so settings are actually updated

current_slot = None # Current game slot, in int from list remaining_slots
previous_slot = None # Previous game slot, in int from list remaining_slots
multiple_slots_remain = True # Makes sure there are slots to swap between
prev_elapsed_time = 0 # Elapsed time before the pause so that it can be added back on after unpause, in seconds
stop_thread = threading.Event() # Init threading event for stopping on complete save
pause_thread = threading.Event() # Init threading event for pausing and unpausing game
sleep_time = 0.1 # Amount of time to sleep, in seconds 
last_swap = 0 # Time when the last swap happened, in unix timestamp
last_finish = 0 # Time when the last save finish happened, in unix timestamp
last_pause = 0 # Time when the last pause happened, in unix timestamp
paused = False # Determines if the shuffler is paused or not, in bool

# Sanity check
if config.PLATFORM_GCN == config.PLATFORM_N64:
    print("[red bold]\n\nCHECK CONFIG.PY\nPLEASE SET 1 AND ONLY 1 OF PLATFORM_N64 AND PLATFORM_GCN TO TRUE\nIF YOU ARE STILL CONFUSED, CHECK README.MD FOR SETUP INSTRUCTIONS AND GENERAL FAQ\n")
    time.sleep(60)
    sys.exit(1)

# Sets seed
if config.SEED != None:
    random.seed(config.SEED)

# Sets up OBS
if config.USING_OBS_WEBSOCKETS:
    client = obs.ReqClient(host=config.OBS_HOST, port=config.OBS_PORT, password=config.OBS_PASSWORD) # Connect to OBS
    client.set_input_settings(config.OBS_TEXT_SOURCE, {"text": config.OBS_TEXT_DISPLAY + str(len(config.remaining_slots))}, False) # Update text source

# Sets up TTS for everything
countdown_nums = ""
for i in reversed(range(1,config.COUNTDOWN+1)):
    if i == 1:
        countdown_nums += str(i)
    else: 
        countdown_nums += f"{i}, "
tts_dict = {
    "finish_save": config.VOICE_TEXT_FINISH_SAVE,
    "last_save": config.VOICE_TEXT_LAST_SAVE,
    "done": config.VOICE_TEXT_DONE,
    "countdown": f"Starting in {countdown_nums}",
    "begin": "Press Spacebar to Begin",
    "paused": "Game Paused",
    "unpaused": "Game Unpaused",
}

def tts(tts_dict, fresh = True, accent = "us"):
    if fresh == True:
        if os.path.exists("tts"):
            shutil.rmtree("tts")
        os.makedirs("tts")
    for title, text in tts_dict.items():
        gTTS(text=text, lang='en', slow=False, tld=accent).save(f"tts/{title}.mp3")

tts(tts_dict)

# Thread function for timer
def print_elapsed_time():
    global start_time, prev_elapsed_time, hours, minutes, seconds
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time + prev_elapsed_time
        hours, rem = divmod(elapsed_time, 3600) # Caluculates hours and remainder to be used in next line
        minutes, seconds = divmod(rem, 60) # Caluculates minutes and seconds
        print(f"Elapsed time: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        time.sleep(1)
        if pause_thread.is_set(): # Saves current time and kills the thread as another thread will be started on unpause
            prev_elapsed_time = elapsed_time
            break

# Helper function to streamline the press and release of keys
def press_and_release(key, timeout=.1):
    keyboard.press(key)
    time.sleep(timeout)
    keyboard.release(key)

# Main function that swaps between the saves
def swap_game():
    global last_swap, current_slot, previous_slot, multiple_slots_remain, paused, run_timer

    #Keeps game paused
    if paused:
        time.sleep(.05)
        return
    
    #Update OBS text
    if config.USING_OBS_WEBSOCKETS:
        client.set_input_settings(config.OBS_TEXT_SOURCE, {"text": config.OBS_TEXT_DISPLAY + str(len(config.remaining_slots))}, False) # Update text source

    # Swap to new slot
    if len(config.remaining_slots) >= 2:
        while True:
            current_slot = random.choice(config.remaining_slots)
            if current_slot != previous_slot: # Make sure the slot isn't the same, otherwise run the while loop again
                previous_slot = current_slot
                break
        press_and_release(current_slot) # Go to active slot (GCN also load the state)
        if config.PLATFORM_N64:
            press_and_release(config.N64_LOAD_STATE) # Load the state in the active slot
        print(f"\nSWAPPING TO SLOT {current_slot}!") # Print the slot
    
    # Stops swapping when 1 slot left
    elif len(config.remaining_slots) == 1 and multiple_slots_remain:
        current_slot = config.remaining_slots[0]
        multiple_slots_remain = False
        press_and_release(current_slot) # Go to active slot (GCN also load the state)
        if config.PLATFORM_N64:
            press_and_release(config.N64_LOAD_STATE) # Load the state in the active slot
        print(f"\nSWAPPING TO SLOT {current_slot}!") # Print the slot
    
    # After 0 saves left
    elif len(config.remaining_slots) == 0:
        pause_thread.set()
        print("[green bold]GAME COMPLETED!")
        playsound(application_path + "\\tts\\done.mp3")
        if config.TIMER:
            if hours > 0:
                timer_str = f"You completed the game in {hours:.0f} hours, {minutes:.0f} minutes, and {seconds:.3f} seconds"
            elif minutes > 0:
                timer_str = f"You completed the game in {minutes:.0f} minutes and {seconds:.3f} seconds"
            else:
                timer_str = f"You completed the game in {seconds:.3f} seconds"
            myobj = gTTS(text=timer_str, lang='en', slow=False)
            myobj.save("tts/timer.mp3")
            print("[green bold]" + timer_str)
            playsound(application_path + "\\tts\\timer.mp3")
        shutil.rmtree("tts")
        time.sleep(30)
        sys.exit(0)
    
    last_swap = time.time() #Store current time to compare against next loop through
    if len(config.remaining_slots) > 1:
        print(f"Remaining Slots: {config.remaining_slots}\n")

    random_time = random.randint(config.MINIMUN_SLOT_TIME,config.MAXIMUM_SLOT_TIME) * (1/sleep_time)
    for i in range(int(random_time)):
        if stop_thread.is_set(): # When space is pressed, break the waiting loop and swap to new save
            break
        time.sleep(sleep_time) # Main waiting chuck between swaps
    
    # Save slot
    if config.PLATFORM_N64:
        press_and_release(config.N64_LOAD_STATE)
    elif config.PLATFORM_GCN:
        press_and_release(f"shift + {current_slot}")
    
    time.sleep(0.1) # Gives it time to save

def keyboard_listener():
    global last_finish, last_pause, current_slot, paused, run_timer, pause_timer
    while True:
        if keyboard.is_pressed(config.FINISH_SAVE_BUTTON):
            if time.time() - last_swap >= 1 and time.time() - last_finish >= config.KEY_COOLDOWN:
                last_finish = time.time()
                if current_slot and current_slot in config.remaining_slots:
                    config.remaining_slots.remove(current_slot)
                    print(f"\nRemoved {current_slot} from Remaining Slots!\n")
                    if len(config.remaining_slots) > 1:
                        playsound(application_path + "\\tts\\finish_save.mp3", False)
                if len(config.remaining_slots) == 1:
                    playsound(application_path + "\\tts\\last_save.mp3", False)
                    pass
                stop_thread.set()
        elif keyboard.is_pressed(config.PAUSE_BUTTON):
            if time.time() - last_pause >= config.KEY_COOLDOWN:
                last_pause = time.time()
                if paused == True:
                    playsound(application_path + "\\tts\\unpaused.mp3", False)
                    print("GAME UNPAUSED")
                    paused = False
                    if config.TIMER:
                        pause_thread.clear()
                        print_thread = threading.Thread(target=print_elapsed_time, daemon=True)
                        print_thread.start()
                    if config.PLATFORM_GCN:
                        press_and_release(config.GCN_PAUSE)
                    elif config.PLATFORM_N64:
                        press_and_release(config.N64_PAUSE)
                elif paused == False:
                    playsound(application_path + "\\tts\\paused.mp3", False)
                    print("GAME PAUSED")
                    paused = True
                    pause_thread.set()
                    if config.PLATFORM_GCN:
                        press_and_release(config.GCN_PAUSE)
                    elif config.PLATFORM_N64:
                        press_and_release(config.N64_PAUSE)
        time.sleep(0.05)

##########################################################################################################################
playsound(application_path + "\\tts\\begin.mp3",False)
time.sleep(.3) # Allows tts time to speak
print("\n[bold]PRESS SPACEBAR TO BEGIN!")
print(f"After you begin, press {config.FINISH_SAVE_BUTTON} to finish a save and press {config.PAUSE_BUTTON} to pause and unpause the shuffler.")
keyboard.wait('space')   

playsound(application_path + "\\tts\\countdown.mp3",False)
for i in reversed(range(config.COUNTDOWN)):
    print(f"\nSTARTING IN {i+1}")
    time.sleep(1)

# Start Timer 
if config.TIMER:
    print_thread = threading.Thread(target=print_elapsed_time, daemon=True)
    print_thread.start()

# Start main loop
while True:
    listener = threading.Thread(target=keyboard_listener, daemon=True)
    listener.start()
    swap_game()
    stop_thread.clear()
