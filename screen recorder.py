import numpy as np
import datetime
import pyautogui
import cv2 as cv
dtstamp=str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
size=pyautogui.size()
video = cv.VideoWriter("Screen Recording {} .avi".format(dtstamp),cv.VideoWriter_fourcc(*'MJPG'),20, size)
print("Recording the Screen - To Stop press 'e' on the Preview Window")
while True:
    screen_shot = pyautogui.screenshot()
    recframe = np.array(screen_shot)
    recframe = cv.cvtColor(recframe, cv.COLOR_BGR2RGB)
    video.write(recframe)
    cv.imshow("Recording Preview (You can Minimize it)", recframe)    
    if cv.waitKey(1) == ord("e"):
        break
cv.destroyAllWindows()
video.release()
