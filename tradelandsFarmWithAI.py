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

collectRocks = False
collectTrees = False

while True:
    user_input = input("Type 'r' to collect rocks, 't' to collect trees, or 'b' to collect both: ").lower()
    
    if user_input == 'r':
        collectRocks = True
        collectTrees = False
        break
    elif user_input == 't':
        collectRocks = False
        collectTrees = True
        break
    elif user_input == 'b':
        collectRocks = True
        collectTrees = True
        break
    else:
        print("Invalid input. Please type 'r', 't', or 'b'.")
        continue

hasWarehouseBot = False
warehouseBotName = ""

while True:
    user_input = input("Do you have a warehouse bot? y/n: ").lower()
    
    if user_input == 'y':
        hasWarehouseBot = True
        break
    elif user_input == 'n':
        hasWarehouseBot = False
        break
    else:
        print("Invalid input. Please type y or n")
        continue

warehouseBotName = input("Type the name of the warehouse bot (not case sensitive): ").lower()
    
    

class WindowCapture:
    w = 0
    h = 0
    hwnd = None

    def __init__(self, window_name):
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))

        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        border_pixels = 8
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

    def get_screenshot(self):
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        img = img[...,:3]
        img = np.ascontiguousarray(img) 
            
        return img

    def generate_image_dataset(self):
        if not os.path.exists("images"):
            os.mkdir("images")
        while(True):
            img = self.get_screenshot()
            im = Image.fromarray(img[..., [2, 1, 0]])
            im.save(f"./images/img_{len(os.listdir('images'))}.jpeg")
            sleep(1)
    
    def get_window_size(self):
        return (self.w, self.h)
    
class ImageProcessor:
    W = 0
    H = 0
    net = None
    ln = None
    classes = {}
    colors = []

    def __init__(self, img_size, cfg_file, weights_file):
        np.random.seed(42)
        self.net = cv.dnn.readNetFromDarknet(cfg_file, weights_file)
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i-1] for i in self.net.getUnconnectedOutLayers()]
        self.W = img_size[0]
        self.H = img_size[1]
        
        with open('yolo-opencv-detector-main/yolov4-tiny/obj.names', 'r') as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            self.classes[i] = line.strip()
        
        # If you plan to utilize more than six classes, please include additional colors in this list.
        self.colors = [
            (0, 255, 0), 
            (0, 0, 255), 
            (255, 0, 0), 
            (255, 255, 0), 
            (255, 0, 255), 
            (0, 255, 255)
        ]
        

    def proccess_image(self, img):

        blob = cv.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.ln)
        outputs = np.vstack(outputs)
        
        coordinates = self.get_coordinates(outputs, 0.5)

        #self.draw_identified_objects(img, coordinates)

        return coordinates

    def get_coordinates(self, outputs, conf):

        boxes = []
        confidences = []
        classIDs = []

        for output in outputs:
            scores = output[5:]
            
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > conf:
                x, y, w, h = output[:4] * np.array([self.W, self.H, self.W, self.H])
                p0 = int(x - w//2), int(y - h//2)
                boxes.append([*p0, int(w), int(h)])
                confidences.append(float(confidence))
                classIDs.append(classID)

        indices = cv.dnn.NMSBoxes(boxes, confidences, conf, conf-0.1)

        if len(indices) == 0:
            return []

        coordinates = []
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            coordinates.append({'x': x, 'y': y, 'w': w, 'h': h, 'class': classIDs[i], 'class_name': self.classes[classIDs[i]]})
        return coordinates

    def draw_identified_objects(self, img, coordinates):
        for coordinate in coordinates:
            x = coordinate['x']
            y = coordinate['y']
            w = coordinate['w']
            h = coordinate['h']
            classID = coordinate['class']
            
            color = self.colors[classID]
            
            cv.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv.putText(img, self.classes[classID], (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv.imshow('DETECTED OBJECTS',  img)


window_name = "Roblox"
cfg_file_name = "./yolo-opencv-detector-main/yolov4-tiny/yolov4-tiny-custom.cfg"
weights_file_name = "yolo-opencv-detector-main/yolov4-tiny-custom_last.weights"

wincap = WindowCapture(window_name)
improc = ImageProcessor(wincap.get_window_size(), cfg_file_name, weights_file_name)

width = 1920
height = 1080



def equipPickaxeIfEmpty():
    try:
        try:
            empty3slot = pyautogui.locateOnScreen("empty3slot.png", grayscale=False, confidence=.99)
        except:
            empty3slotRed = pyautogui.locateOnScreen("empty3slotRed.png", grayscale=False, confidence=.99)
            pydirectinput.press('3')
        
        #scroll out just a bit in case you're zoomed in
        pyautogui.scroll(-100)
        sleep(.25)
        pyautogui.scroll(-100)
        sleep(.25)
        pyautogui.scroll(-100)
        sleep(.25)
        pyautogui.scroll(-100)
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
                #find a pickaxe
                ironPickaxe = pyautogui.locateOnScreen("pickaxe.png", confidence=.9)
                centeredIronPickaxe = pyautogui.center(ironPickaxe)
                pydirectinput.moveTo(int(centeredIronPickaxe.x + 10), int(centeredIronPickaxe.y))
                pydirectinput.moveTo(int(centeredIronPickaxe.x), int(centeredIronPickaxe.y))
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
        

        pydirectinput.press('g')
        sleep(1)
        
    except Exception as e:
        print(f"An exception occurred: {e}")

def depositAndGetTools():
    trading = True
    while (trading):
        try:
            #PYDIRECTINPUT CANT TYPE A FUCKING UNDERSCORE SO WE HAVE TO STOP TYPING THE NAME IF WE GET A FUCKING UNDERSCORE
            chatMessage = f"//trade {warehouseBotName}"
            for i in range(0, len(chatMessage)):
                if (chatMessage[i] == "_"):
                    break
                else:
                    pydirectinput.press(chatMessage[i])
                sleep(.1)
            pydirectinput.press('enter')
            sleep(5)

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

            woods = ["ash.png", "cherry.png", "ebony.png", "elm.png", "ironwood.png", "mahogany.png", "oak.png"]
            tradedAlready = [False, False, False, False, False, False, False]

            scrolls = 0
            searchingForItem = True
            while searchingForItem:
                #scroll down list of items, sleep to wait for scroll animation to finish
                pyautogui.scroll(-100)
                sleep(.25)

                for i in range(0, len(woods)):
                    if (not tradedAlready[i]):
                        try:
                            item = pyautogui.locateOnScreen(woods[i], confidence=.9)
                            centeredItem = pyautogui.center(item)
                            pydirectinput.moveTo(int(centeredItem.x + 10), int(centeredItem.y))
                            pydirectinput.moveTo(int(centeredItem.x), int(centeredItem.y))
                            pydirectinput.click()
                            tradedAlready[i] = True
                            sleep(.25)
                            allButton = pyautogui.locateOnScreen("all.png", confidence=.9)
                            centeredAllButton = pyautogui.center(allButton)
                            pydirectinput.moveTo(int(centeredAllButton.x + 10), int(centeredAllButton.y))
                            pydirectinput.moveTo(int(centeredAllButton.x), int(centeredAllButton.y))
                            pydirectinput.click()
                            
                        except:
                            print("Item not seen in gui")

                scrolls += 1
                if (scrolls > 10):
                    searchingForItem = False
                    
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
            
            trading = False
            sleep(5)
            
        except Exception as e:
            print(f"An exception occurred: {e}")

def equipAxeIfEmpty():
    try:
        try:
            empty2slot = pyautogui.locateOnScreen("empty2slot.png", grayscale=False, confidence=.99)
        except:
            empty2slotRed = pyautogui.locateOnScreen("empty2slotRed.png", grayscale=False, confidence=.99)
            pydirectinput.press('2')

        
        #scroll out just a bit in case you're zoomed in
        pyautogui.scroll(-100)
        sleep(.25)
        pyautogui.scroll(-100)
        sleep(.25)
        pyautogui.scroll(-100)
        sleep(.25)
        pyautogui.scroll(-100)
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

        numScrolls = 0
        searchingForTool = True
        while searchingForTool:
            try:
                #scroll down list of items, sleep to wait for scroll animation to finish
                pyautogui.scroll(-100)
                numScrolls += 1
                
                if (numScrolls > 10):
                    pydirectinput.press('g')
                    depositAndGetTools()
                    pydirectinput.press('g')

                sleep(.25)
                #find an axe
                ironAxe = pyautogui.locateOnScreen("axe.png", confidence=.9)
                centeredIronAxe = pyautogui.center(ironAxe)
                pydirectinput.moveTo(int(centeredIronAxe.x + 10), int(centeredIronAxe.y))
                pydirectinput.moveTo(int(centeredIronAxe.x), int(centeredIronAxe.y))
                pydirectinput.click()
                #find the equip slot
                equipRightHip = pyautogui.locateOnScreen("equipRightHip.png", confidence=.9)
                centeredEquipRightHip = pyautogui.center(equipRightHip)
                pydirectinput.moveTo(int(centeredEquipRightHip.x + 10), int(centeredEquipRightHip.y))
                pydirectinput.moveTo(int(centeredEquipRightHip.x), int(centeredEquipRightHip.y))
                pydirectinput.click()
                searchingForTool = False
            except:
                print("No tool to equip")
        

        pydirectinput.press('g')
        sleep(1)
        
        
    except Exception as e:
        print(f"An exception occurred: {e}")

def findAndGatherResource():
    #scroll in to begin looking for resource
    for i in range(0,25):
        sleep(.1)
        pyautogui.scroll(100)

    sleep(1)
    resource = None

    #jumps when this % 10 == 0
    jumpCounter = 0

    mouseX = int(width/2)
    mouseY = int(height/2)  
    pydirectinput.moveTo(int(mouseX), int(mouseY))

    finding = True
    while(finding):
        
        ss = wincap.get_screenshot()

        coordinates = improc.proccess_image(ss)
        #print(coordinates)
        #sleep(.25)
        coordinates = [c for c in coordinates if (c["class_name"] == "rock" and collectRocks) or (c["class_name"] == "tree" and collectTrees)]
        
        #if there are no resources, spazz and look everywhere randomly
        if len(coordinates) == 0:
            mouseX += 10
            mouseY += random.randint(1,30) - 15
            pydirectinput.moveTo(int(mouseX), int(mouseY))
            continue
        
        resource = None

        #if there is more than one resource on screen, pick the one that is closest to the center of the screen so juggling doesn't occur
        if len(coordinates) == 1:
            resource = coordinates[0]
        else:
            indexOfClosestResource = 0
            biggestResourceSize = coordinates[0]['w']*coordinates[0]['h']

            for i in range(1, len(coordinates)):
                resourceSize = coordinates[i]['w']*coordinates[i]['h']
                if resourceSize > 1.5*biggestResourceSize:
                    indexOfClosestResource = i
                    biggestResourceSize = resourceSize
            
            resource = coordinates[indexOfClosestResource]

            """ indexOfClosestResource = 0
            closestToScreenCenter = math.sqrt(((coordinates[0]['x'] + coordinates[0]['w']/2) - width/2)**2 + ((coordinates[0]['y'] + coordinates[0]['h']/2) - height/2)**2)

            for i in range(1, len(coordinates)):
                resourceDist = math.sqrt(((coordinates[i]['x'] + coordinates[i]['w']/2) - width/2)**2 + ((coordinates[i]['y'] + coordinates[i]['h']/2) - height/2)**2)
                if resourceDist < closestToScreenCenter:
                    indexOfClosestResource = i
                    closestToScreenCenter = resourceDist
            
            resource = coordinates[indexOfClosestResource] """

        
        #print(rock)

        #make the mouse movement more aggressive if closer
        mouseMovement = 50
        """ if (resource['w']*resource['h'] > width*height/10):
            mouseMovement = 50
        else:
            mouseMovement = 60 """

        #align the resource to the center of the screen
        pixDistX = ((resource['x'] + resource['w']/2) - width/2)
        pixDistY = ((resource['y'] + resource['h']/2) - height/2)
        print(pixDistX, pixDistY)
        for i in range(0, int( abs(pixDistX) / mouseMovement)):
            mouseX += -1 if pixDistX < 0 else 1
            pydirectinput.moveTo(int(mouseX), int(mouseY))

        for i in range(0, int(abs(pixDistY) / mouseMovement)):
            mouseY += -1 if pixDistY < 0 else 1
            pydirectinput.moveTo(int(mouseX), int(mouseY))

        #stop finding when the rock takes up a significant part of the screen
        if ( (resource["class_name"] == "tree" and resource['w']*resource['h'] > width*height/5) or (resource["class_name"] == "rock" and resource['w']*resource['h'] > width*height/6) ):
            finding = False
            break
        
        # walking. Go slower if we're close to maintain precision
        pydirectinput.keyDown('w')

        # jump occasionally
        jumpCounter += 1
        if (jumpCounter % 10 == 0):
            pydirectinput.press('space')

        if ( (resource["class_name"] == "tree" and resource['w']*resource['h'] > width*height/20) or (resource["class_name"] == "rock" and resource['w']*resource['h'] > width*height/30)):
            sleep(.02)
        else:
            sleep(.5)

        pydirectinput.keyUp('w')

        

    #gather the resource
    key = ''
    if (resource["class_name"] == "rock"):
        key = '3'
    elif (resource["class_name"] == "tree"):
        key = '2'

    pydirectinput.press(key)
    for i in range(0,40):
        pydirectinput.click()
        sleep(.75)

    #scroll in to begin looking for rock
    pydirectinput.press(key)
    sleep(.25)
    for i in range(0,10):
        sleep(.1)
        pyautogui.scroll(100)

        
sleep(3)

while True:
    if collectRocks:
        equipPickaxeIfEmpty()
    
    if collectTrees:
        equipAxeIfEmpty()

    findAndGatherResource()


