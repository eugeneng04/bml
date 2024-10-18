import cv2.aruco as cv2
import cv2
import utils_data_process
import queue
import video
from run_stm_12 import *
import threading
import numpy as np

tags = [3, 4, 10, 5]
tag_mapping = {}
for i in range(len(tags)):
    tag_mapping[i] = tags[i]

default_states = np.array([90, 180, 90, 90])

def normalize_angle(angle):
    return float((angle + 180) % 360 - 180)

def angle_loop(frameQ, outputQ, scale):
    aruco_detector.add_queue(frameQ)
    base_tag = 2
    first_frame = True
    while not cameraStop.is_set():
        corners, ids = frameQ.get()
        #print(corners, ids)
        angle_dict = {}
        if ids is not None:
            if first_frame and (2 in ids): # get the scale
                base_index = np.where(ids == base_tag)[0][0]
                pxl_scale = video.pixelToMM(corners[base_index], 4.5) # change size of artag here
                first_frame = False
                scale.append(pxl_scale)

            for i, marker_corners in enumerate(corners):
                angle_wrt_horiz = utils_data_process.calc_angle_wrt_horiz(marker_corners[0])
                marker_id = ids[i][0]
                angle_dict[marker_id] = angle_wrt_horiz
        
        #ordered_angles = np.array([tag for tag, _ in sorted(tag_mapping.items(), key=lambda item: item[1])])
        ordered_angles = np.array([])
        try:
            for i in range(len(tag_mapping)):
                angle = angle_dict[tag_mapping[i]]
                ordered_angles = np.append(ordered_angles, angle)
            ordered_angles -= default_states
            relative_angles = np.diff(ordered_angles, prepend=0)
            relative_angles = list(map(normalize_angle, relative_angles))
        except:
            pass
            
        if len(relative_angles == 4):
            outputQ.put(relative_angles)
def camera_loop(frameQ, ):
    #file = "./data-raw/Actuator5And6 IncrementOf5/output_video_0.avi"
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        corners, ids, c = video.detect_aruco_tag(frame)
        
        if ids is not None:
            #print(corners)
            frameQ.put((corners, ids))
    cameraStop.set()
    

if __name__ == "__main__":
    cameraStop = threading.Event()
    cameraStop.clear()
    frameQ = queue.Queue()
    angle_thread = threading.Thread(target = angle_loop, args = ((frameQ, None, None), ))
    camera_thread = threading.Thread(target = camera_loop, args = ((frameQ),))
    camera_thread.start()
    angle_thread.start()
    # camera_loop(frameQ)
    # print("done")
    # angle_loop(frameQ)
