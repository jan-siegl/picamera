import numpy as np
from camera import get_rtsp_url
import cv2 as cv
import time
from datetime import datetime
from pathlib import Path

img_dir = Path('./testimg/')

cap = cv.VideoCapture(get_rtsp_url())

prev_frame_time = 0
# used to record the time at which we processed current frame
new_frame_time = 0
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
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

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
    cv.putText(gray, fps, (7, 70), font, 3, (100, 255, 0), 3, cv.LINE_AA)

    #Bounding box
    start_point = (350, 150)
        # Ending coordinate, here (220, 220)
        # represents the bottom right corner of rectangle
    end_point = (850, 500)
        # Blue color in BGR
    color = (255, 0, 0)
        # Line thickness of 2 px
    thickness = 2
    cv.rectangle(gray, start_point, end_point, color, thickness)

    # Display the resulting frame
    cv.imshow('frame', gray)

    if cv.waitKey(1) == ord('p'):
        now = datetime.now()
        filename = now.strftime("%m-%d-%Y_%H-%M-%S-%f") + ".jpg"
        filepath = img_dir / filename
        cv.imwrite(str(filepath), frame)

    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()