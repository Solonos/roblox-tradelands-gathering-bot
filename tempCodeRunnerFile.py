#find the submit button slot
                submitButton = pyautogui.locateOnScreen("submit.png", confidence=.9)
                centeredSubmitButton = pyautogui.center(submitButton)
                pydirectinput.moveTo(int(centeredSubmitButton.x + 10), int(centeredSubmitButton.y))
                pydirectinput.moveTo(int(centeredSubmitButton.x), int(centeredSubmitButton.y))
                pydirectinput.click()
                #find the accept button
                acceptButton = pyautogui.locateOnScreen("accept.png", confidence=.9)
                centeredAcceptButton = pyautogui.center(acceptButton)
                pydirectinput.moveTo(int(centeredAcceptButton.x + 10), int(centeredAcceptButton.y))
                pydirectinput.moveTo(int(centeredAcceptButton.x), int(centeredAcceptButton.y))
                pydirectinput.click()
                searchingForTool = False
                sleep(5)