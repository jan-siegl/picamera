from datetime import datetime, timedelta
import cv2
import time
import sys
import numpy as np
from camera import get_rtsp_url

def build_model(is_cuda):
    net = cv2.dnn.readNet("yolov5s.onnx")
    if is_cuda:
        print("Attempty to use CUDA")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
    else:
        print("Running on CPU")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    return net

INPUT_WIDTH = 640
INPUT_HEIGHT = 640
SCORE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
CONFIDENCE_THRESHOLD = 0.8

def detect(image, net):
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (INPUT_WIDTH, INPUT_HEIGHT), swapRB=True, crop=False)
    net.setInput(blob)
    preds = net.forward()
    return preds

def load_capture():
    #capture = cv2.VideoCapture(get_rtsp_url())
    capture = cv2.VideoCapture("testVideo/vaha-prujezd.mp4")
    return capture

def load_classes():
    class_list = []
    with open("classes.txt", "r") as f:
        class_list = [cname.strip() for cname in f.readlines()]
    return class_list

class_list = load_classes()

def wrap_detection(input_image, output_data):
    class_ids = []
    confidences = []
    boxes = []

    rows = output_data.shape[0]

    image_width, image_height, _ = input_image.shape

    x_factor = image_width / INPUT_WIDTH
    y_factor =  image_height / INPUT_HEIGHT

    for r in range(rows):
        row = output_data[r]
        confidence = row[4]
        if confidence >= 0.4:

            classes_scores = row[5:]
            _, _, _, max_indx = cv2.minMaxLoc(classes_scores)
            class_id = max_indx[1]
            if (classes_scores[class_id] > .25):

                confidences.append(confidence)

                class_ids.append(class_id)

                x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item()
                left = int((x - 0.5 * w) * x_factor)
                top = int((y - 0.5 * h) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                box = np.array([left, top, width, height])
                boxes.append(box)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.45)

    result_class_ids = []
    result_confidences = []
    result_boxes = []

    for i in indexes:
        result_confidences.append(confidences[i])
        result_class_ids.append(class_ids[i])
        result_boxes.append(boxes[i])

    return result_class_ids, result_confidences, result_boxes

def format_yolov5(frame):

    row, col, _ = frame.shape
    _max = max(col, row)
    result = np.zeros((_max, _max, 3), np.uint8)
    result[0:row, 0:col] = frame
    return result

last_time = datetime.strptime("2023-06-07 15:37:24.455308", '%Y-%m-%d %H:%M:%S.%f')

def set_time():
    global last_time
    last_time = datetime.now() + timedelta(seconds=30)

set_time()

def take_snapshot():
    if datetime.now() > last_time:
        print ("doubleYes")
        set_time()
    else:
        print ("no")



colors = [(255, 255, 0), (0, 255, 0), (0, 255, 255), (255, 0, 0)]

is_cuda = len(sys.argv) > 1 and sys.argv[1] == "cuda"

net = build_model(is_cuda)
capture = load_capture()


start = time.time_ns()
frame_count = 0
total_frames = 0
fps = -1

fpsLimit = 0.25 # throttle limit
startTime = time.time()

while True:

    nowTime = time.time()
    #print(fpsLimit)

    _, frame = capture.read()
    if frame is None:
        print("End of stream")
        break
    if (nowTime - startTime) > fpsLimit:
        #print(nowTime)
        inputImage = format_yolov5(frame)
        outs = detect(inputImage, net)

        class_ids, confidences, boxes = wrap_detection(inputImage, outs[0])

        frame_count += 1
        total_frames += 1

        for (classid, confidence, box) in zip(class_ids, confidences, boxes):
            color = colors[int(classid) % len(colors)]
            cv2.rectangle(frame, box, color, 2)
            if (box[0] > 300 and box[1] > 120 and (box[0] + box[2]) < 850 and (box[1] + box[3]) < 500):
                print("yes")
                take_snapshot()
            #print((box[0] + box[2]), (box[1] + box[3]))
            #print(box)
            cv2.rectangle(frame, (box[0], box[1] - 20), (box[0] + box[2], box[1]), color, -1)
            cv2.putText(frame, class_list[classid], (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0))

        if frame_count >= 30:
            end = time.time_ns()
            fps = 1000000000 * frame_count / (end - start)
            frame_count = 0
            start = time.time_ns()

        if fps > 0:
            fps_label = "FPS: %.2f" % fps
            cv2.putText(frame, fps_label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            #Bounding box
        #start_point = (350, 150)
        start_point = (300, 120)
                # Ending coordinate, here (220, 220)
                # represents the bottom right corner of rectangle
        #end_point = (850, 500)
        end_point = (850, 500)
                # Blue color in BGR
        color = (255, 255, 255)
                # Line thickness of 2 px
        thickness = 2
        cv2.rectangle(frame, start_point, end_point, color, thickness)

        cv2.imshow("output", frame)


    if cv2.waitKey(1) > -1:
        print("finished by user")
        break

print("Total frames: " + str(total_frames))