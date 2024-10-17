import cv2.aruco as cv2
import cv2
import utils_data_process
import queue
import video
#from run_stm_12 import *
import threading
import numpy as np

tag_dict = {4: 0, # key: actual tag, value = index of robot
            2: 1,
            3: 2,
            17: 3,
            10: 4,
            5: 5}

default_states = np.array([90, 90, 0, 0, -180, 0])

def angle_loop(frameQ):

    while not cameraStop.is_set():
        corners, ids = frameQ.get()
        #print(corners, ids)
        angle_dict = {}
        if ids is not None:
            for i, marker_corners in enumerate(corners):
                angle_wrt_horiz = utils_data_process.calc_angle_wrt_horiz(marker_corners[0])
                marker_id = ids[i][0]
                angle_dict[marker_id] = angle_wrt_horiz
        
        ordered_angles = np.array([angle_dict[tag] for tag, _ in sorted(tag_dict.items(), key=lambda item: item[1])]) - default_states
        relative_angles = np.diff(ordered_angles)

        print(relative_angles)

def camera_loop(frameQ, ):
    file = "./data-raw/Actuator5And6 IncrementOf5/output_video_0.avi"
    cap = cv2.VideoCapture(file)
    
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
    angle_thread = threading.Thread(target = angle_loop, args = ((frameQ), ))
    camera_thread = threading.Thread(target = camera_loop, args = ((frameQ),))
    camera_thread.start()
    angle_thread.start()
    # camera_loop(frameQ)
    # print("done")
    # angle_loop(frameQ)
