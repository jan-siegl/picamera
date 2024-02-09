import numpy as np
from camera import get_rtsp_url
import cv2 as cv
import time
from datetime import datetime
from pathlib import Path
import savePicture

import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


def detect_7_segments(image):
    config = '--psm 6 -c tessedit_char_whitelist="0123456789 "'
    return pytesseract.image_to_string(image, lang='eng', config=config)

def getNum(segments):
        # hardcoding outputs
        if segments == [0, 2, 3, 4, 5, 6]:
            return 0;
        if segments == [5, 6]:
            return 1;
        if segments == [0, 1, 2, 4, 5]:
            return 2;
        if segments == [0, 1, 2, 5, 6]:
            return 3;
        if segments == [1, 3, 5, 6]:
            return 4;
        if segments == [0, 1, 2, 3, 6]:
            return 5;
        if segments == [0, 1, 2, 3, 4, 6]:
            return 6;
        if segments == [0, 5, 6]:
            return 7;
        if segments == [0, 1, 2, 3, 4, 5, 6]:
            return 8;
        if segments == [0, 1, 2, 3, 5, 6]:
            return 9;
        # ERROR
        return -1;


img_dir = Path('./testimg/')

cap = cv.VideoCapture(get_rtsp_url())

prev_frame_time = 0
# used to record the time at which we processed current frame
new_frame_time = 0

prev_prev_tSymbol = 0
prev_tSymbol = 0
prev_measurment = 0
prev_finalNumber = 0
prev_prev_finalNumber = 0

frame_count = 0

if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    frame_count += 1
    if frame_count > 30:
        frame_count = 0
        # Our operations on the frame come here
        #cropped_image = frame[40:450, 825:1750]
        cropped_image = frame[20:450, 525:1750]
        gray = cv.cvtColor(cropped_image, cv.COLOR_BGR2GRAY)
        thresh = gray
        #ret, thresh = cv.threshold(gray, 60, 255, cv.THRESH_BINARY)

        tSymbol = thresh[225, 885] # t symbol location

        #second decimal
        sDecSegments = []
        if thresh[120, 700] == 255: 
            sDecSegments.append(0)
        if thresh[255, 660] == 255: 
            sDecSegments.append(1)
        if thresh[385, 620] == 255: 
            sDecSegments.append(2)
        if thresh[160, 620] == 255: 
            sDecSegments.append(3)
        if thresh[350, 565] == 255: 
            sDecSegments.append(4)
        if thresh[200, 730] == 255: 
            sDecSegments.append(5)
        if thresh[330, 695] == 255: 
            sDecSegments.append(6)

        sDecNumber = getNum(sDecSegments)

        

        #first decimal
        fDecSegments = []
        if thresh[80, 460] == 255: 
            fDecSegments.append(0)
        if thresh[220, 420] == 255: 
            fDecSegments.append(1)
        if thresh[370, 380] == 255: 
            fDecSegments.append(2)
        if thresh[130, 375] == 255: 
            fDecSegments.append(3)
        if thresh[255, 330] == 255: 
            fDecSegments.append(4)
        if thresh[160, 515] == 255: 
            fDecSegments.append(5)
        if thresh[300, 475] == 255: 
            fDecSegments.append(6)

        fDecNumber = getNum(fDecSegments)
    

        #tons 
        #first decimal
        tonsSegments = []
        if thresh[40, 195] == 255: 
            tonsSegments.append(0)
        if thresh[190, 150] == 255: 
            tonsSegments.append(1)
        if thresh[345, 110] == 255: 
            tonsSegments.append(2)
        if thresh[95, 100] == 255: 
            tonsSegments.append(3)
        if thresh[265, 45] == 255: 
            tonsSegments.append(4)
        if thresh[120, 255] == 255: 
            tonsSegments.append(5)
        if thresh[285, 205] == 255: 
            tonsSegments.append(6)

        tonsNumber = getNum(tonsSegments)
        if tonsNumber != -1 and fDecNumber != -1 and sDecNumber != -1 and tSymbol == 255 and prev_tSymbol == 255 and prev_prev_tSymbol == 255:
            finalNumber = float(str(tonsNumber) + "." + str(fDecNumber) + str(sDecNumber))
            #check if it is the same measurment for at least 3 * checked frames (if each 60th frame on 30 fps camera that means 6 seconds )
            if finalNumber == prev_finalNumber and finalNumber == prev_prev_finalNumber:
                #check if it is not still the same measurment
                if finalNumber > 0 and finalNumber != prev_measurment and abs(finalNumber - prev_measurment) > 0.02:
                
                    print(str(finalNumber) + " t")
                    savePicture.savePicture(finalNumber)

                prev_measurment = finalNumber

            prev_prev_finalNumber = prev_finalNumber
            prev_finalNumber = finalNumber
        
        prev_prev_tSymbol = prev_tSymbol
        prev_tSymbol = tSymbol
        

        #hex = (color[0] << 16) + (color[1] << 8) + (color[2])
        #print(tSymbol)


        #print("Vaha:", detect_7_segments(frame).replace('\f', '').replace('\n', ''))

        #FPS
            # font which we will be using to display FPS
        font = cv.FONT_HERSHEY_SIMPLEX
            # time when we finish processing for this frame
        new_frame_time = time.time()
            # Calculating the fps
            # fps will be number of frame processed in given time frame
            # since their will be most of time error of 0.001 second
            # we will be subtracting it to get more accurate result
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
            # converting the fps into integer
        fps = int(fps)
            # converting the fps to string so that we can display it on frame
            # by using putText function
        fps = str(fps)
            # putting the FPS count on the frame
        #cv.putText(gray, fps, (7, 70), font, 3, (100, 255, 0), 3, cv.LINE_AA)

        #Bounding box
        # for t = start_point = (825, 150) end_point = (920, 370)
        start_point = (825, 150)
            # Ending coordinate, here (220, 220)
            # represents the bottom right corner of rectangle
        end_point = (920, 370)
            # Blue color in BGR
        color = (255, 0, 0)
            # Line thickness of 2 px
        thickness = 2
        cv.rectangle(thresh, start_point, end_point, color, thickness)

        # Display the resulting frame
        cv.imshow('frame', thresh )

        if cv.waitKey(1) == ord('p'):
            now = datetime.now()
            filename = now.strftime("%m-%d-%Y_%H-%M-%S-%f") + ".jpg"
            filepath = img_dir / filename
            cv.imwrite(str(filepath), thresh)

        if cv.waitKey(1) == ord('q'):
            break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()