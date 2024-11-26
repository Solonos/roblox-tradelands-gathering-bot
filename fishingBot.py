import numpy as np
import sounddevice as sd
import keyboard
import os
from time import sleep
import time
import pyautogui
import pydirectinput
import keyboard

#program exits when you press '0'
def exit_program():
    os._exit(0)

keyboard.add_hotkey('0', exit_program)



width = 1920
height = 1080
twitchCounter = 0


def equipRodIfEmpty():
    try:
        try:
            empty3slot = pyautogui.locateOnScreen("empty3slot.png", grayscale=False, confidence=.99)
            pydirectinput.press('3')
            sleep(1)
            pydirectinput.press('3')
        except:
            empty3slotRed = pyautogui.locateOnScreen("empty3slotRed.png", grayscale=False, confidence=.99)
            pydirectinput.press('3')

        

        pydirectinput.press('g')
        
        #IMPORTANT- note that you HAVE to use 2 moveTo's so roblox's retarded fucking guis can register that a mouse is hovering over shit
        # And you HAVE to add an offset to the first moveTo for some reason
        pydirectinput.moveTo(int(width/2) + 10, int(height/2))
        pydirectinput.moveTo(int(width/2), int(height/2))

        # scroll to the top of the inventory just in case we're already scrolled down a bit
        pyautogui.scroll(100)
        sleep(.25)
        pyautogui.scroll(100)
        sleep(.25)
        pyautogui.scroll(100)
        sleep(.25)

        searchingForTool = True
        while searchingForTool:
            try:
                #scroll down list of items, sleep to wait for scroll animation to finish
                pyautogui.scroll(-100)
                

                sleep(.25)
                #find a rod
                rod = pyautogui.locateOnScreen("fishingRod.png", confidence=.9)
                centeredRod = pyautogui.center(rod)
                pydirectinput.moveTo(int(centeredRod.x + 10), int(centeredRod.y))
                pydirectinput.moveTo(int(centeredRod.x), int(centeredRod.y))
                pydirectinput.click()
                #find the equip slot
                equipBack = pyautogui.locateOnScreen("equipBack.png", confidence=.9)
                centeredEquipBack = pyautogui.center(equipBack)
                pydirectinput.moveTo(int(centeredEquipBack.x + 10), int(centeredEquipBack.y))
                pydirectinput.moveTo(int(centeredEquipBack.x), int(centeredEquipBack.y))
                pydirectinput.click()
                searchingForTool = False
            except:
                print("No tool to equip")
                return False
        

        pydirectinput.press('g')
        sleep(1)
        pydirectinput.press('3')
        return True
        
        
        
    except Exception as e:
        print(f"An exception occurred: {e}")
        return False


# start of the program
sleep(3)
if (not equipRodIfEmpty()):
    pydirectinput.press('3')
sleep(1)
timeOfLastLoudSound = time.time()
pydirectinput.click()

# Function to handle loud sound events
def on_loud_sound(indata, frames, timeIdk30, status):
    global twitchCounter
    global timeOfLastLoudSound
    try:
        # Compute the RMS (root-mean-square) of the audio signal
        rms = np.sqrt(np.mean(indata**2))
        # Convert RMS to decibels
        rms_db = 20 * np.log10(rms)
        # Check if the sound level exceeds the threshold
        if rms_db > threshold_db:
            print("Loud sound detected!")
            print(rms_db)
            timeOfLastLoudSound = time.time()

            # Reel in fish
            pydirectinput.click()
            sleep(1)
            equipRodIfEmpty()
            sleep(1)
            #twitch
            twitchCounter += 1
            if (twitchCounter % 10 == 0):
                pydirectinput.keyDown('w')
                sleep(2)
                pydirectinput.keyUp('w')
                pydirectinput.keyDown('s')
                sleep(.5)
                pydirectinput.keyUp('s')

            # Cast again
            pydirectinput.click()
    except Exception as e:
        print(f"An exception occurred: {e}")
    


# Set the sample rate and duration for audio recording
sample_rate = 44100
duration = 1  # Duration of each audio recording (in seconds)

# Set the threshold for loud sounds (in decibels)
threshold_db = -35

# Initialize audio input stream outside the loop
with sd.InputStream(callback=on_loud_sound, channels=1, samplerate=sample_rate):
    try:
        # Main loop to keep the program running
        while True:
            # Add a small delay between iterations to reduce resource usage
            sleep(0.1)
            currentTime = time.time()
            print(currentTime - timeOfLastLoudSound)
            if (currentTime - timeOfLastLoudSound > 20):
                timeOfLastLoudSound = currentTime
                pydirectinput.click()
    except KeyboardInterrupt:
        pass  # Exit the loop if '0' is pressed
    except Exception as e:
        print(f"An exception occurred: {e}")