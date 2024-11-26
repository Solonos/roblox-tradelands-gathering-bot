import pyautogui
import pydirectinput
import keyboard
import sys
import os
import random
import math

import numpy as np
import win32gui, win32ui, win32con
from PIL import Image
from time import sleep, time
import cv2 as cv
import random




#program exits when you press '0'
def exit_program():
    os._exit(0)

keyboard.add_hotkey('0', exit_program)


width = 1920
height = 1080


def reapAndReload():
    try:
        tradeRequest = pyautogui.locateOnScreen("wantsToTrade.png", confidence=.9)

        #accept request
        acceptButton = pyautogui.locateOnScreen("accept.png", confidence=.9)
        centeredAcceptButton = pyautogui.center(acceptButton)
        pydirectinput.moveTo(int(centeredAcceptButton.x + 10), int(centeredAcceptButton.y))
        pydirectinput.moveTo(int(centeredAcceptButton.x), int(centeredAcceptButton.y))
        pydirectinput.click()

        sleep(.5)

        # get the mouse into the inventory gui
        pydirectinput.moveTo(int(width/2) + 60, int(height/2))
        pydirectinput.moveTo(int(width/2) + 50, int(height/2))

        # scroll to the top of the inventory just in case we're already scrolled down a bit
        pyautogui.scroll(100)
        sleep(.25)
        pyautogui.scroll(100)
        sleep(.25)
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
                #find an axe
                ironAxe = pyautogui.locateOnScreen("axe.png", confidence=.9)
                centeredIronAxe = pyautogui.center(ironAxe)
                pydirectinput.moveTo(int(centeredIronAxe.x + 10), int(centeredIronAxe.y))
                pydirectinput.moveTo(int(centeredIronAxe.x), int(centeredIronAxe.y))
                pydirectinput.click()
                #find the submit button slot
                submitButton = pyautogui.locateOnScreen("submit.png", confidence=.9)
                centeredSubmitButton = pyautogui.center(submitButton)
                pydirectinput.moveTo(int(centeredSubmitButton.x + 10), int(centeredSubmitButton.y))
                pydirectinput.moveTo(int(centeredSubmitButton.x), int(centeredSubmitButton.y))
                pydirectinput.click()
                sleep(.5)
                #find the accept button
                acceptButton = pyautogui.locateOnScreen("accept.png", confidence=.9)
                centeredAcceptButton = pyautogui.center(acceptButton)
                pydirectinput.moveTo(int(centeredAcceptButton.x + 10), int(centeredAcceptButton.y))
                pydirectinput.moveTo(int(centeredAcceptButton.x), int(centeredAcceptButton.y))
                pydirectinput.click()
                searchingForTool = False
                sleep(5)
            except:
                print("No tool to equip")
        
        
    except Exception as e:
        pydirectinput.keyDown('w')
        sleep(2)
        pydirectinput.keyUp('w')
        pydirectinput.keyDown('s')
        sleep(2)
        pydirectinput.keyUp('s')
        print(f"An exception occurred: {e}")


sleep(3)

while True:
    reapAndReload()


