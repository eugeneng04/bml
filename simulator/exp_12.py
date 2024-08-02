import time
import numpy as np
from run_stm_12 import *
import argparse
import utils_file

camStop = threading.Event()
camStop.clear()
video = cv2.VideoCapture(0)

def cameraThread():
    if (video.isOpened() == False):  
        print("Error reading video file") 
     
    frame_width = int(video.get(3)) 
    frame_height = int(video.get(4)) 
    
    size = (frame_width, frame_height) 

    result = cv2.VideoWriter(f'{folder_name}/recording.avi',  
                            cv2.VideoWriter_fourcc(*'MJPG'), 
                            10, size) 
    while not camStop:
        ret, frame = video.read() 
  
        if ret == True:  
            result.write(frame) 

            cv2.imshow('Frame', frame) 

    video.release() 
    result.release() 

def control_loop(q_output, result_folder): 
    #camera stuff
    camThread = threading.Thread(group=None, target=cameraThread, name="cameraThread")
    camThread.daemon = False  # want clean file close
    #camThread.start()

    global regulator_vals, solenoid_vals
    global charStart
    i = 0
    state = StateStruct()
    print('control_loop- waiting for STM32READY\n')
    time.sleep(1)    # check periodically for start    
    while controlStop.is_set():
        time.sleep(1)    # check periodically for start    
    makeCmd('PRNWAIT', 1000)   # set wait time for state update in ms
    time.sleep(3)
    print('control_loop: started thread')
    time_per_step = 15

    while (not controlStop.is_set()):
        if not stateQ.empty():
            if not charStart.is_set():
                makePressureCmd()
                time.sleep(1)  # should run at state update rate                
            else:
                print("characterization starts")
                for i in range(4): # 4 actuators
                    for j in range(1): #we want to do this 1 times
                        for k in range(2):
                            pattern_arr = [0, 5, 10, 15, 20, 25, 30, 35]
                            for val in pattern_arr:
                                regulator_vals = np.zeros(12)

                                regulator_vals[2*i + k] = val

                                makePressureCmd()
                                time.sleep(time_per_step)
                                ret, frame = video.read()
                                if not ret:
                                    print("failed to grab frame")
                                    break
                                img_name = f"{folder_name}/capture_{2*i+k}_{val}_psi_{j}.png"
                                cv2.imwrite(img_name, frame)

                                if controlStop.is_set():
                                    break
                                if controlStop.is_set():
                                    break
                
                charStart.clear()
                controlStop.set() # stop program after done characterization
        else:
#            print('stateQ empty')
            # print("waiting for characterization start")
            time.sleep(1)

    print('control_loop: finished thread')
    camStop.set() # custom camera thread
    cameraStop.set()

if __name__ == '__main__':
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser()

    parser.add_argument("name", help = "folder for name of file")
    parser.add_argument("--dump", action="store_false", help = "whether to use saved output")
    folder_name = f"{utils_file.getCurrPath()}/logs/{parser.parse_args().name}"

    flag = utils_file.validData(folder_name, "pattern")

    # for i in range(4): # 4 actuators
    #     for j in range(1): #we want to do this 1 times
    #         for k in range(2):
    #             pattern_arr = [0, 5, 10, 15, 20, 25, 30, 35]
    #             for val in pattern_arr:
    #                 regulator_vals = np.zeros(12)

    #                 regulator_vals[2*i + k] = val
    #                 print(regulator_vals)
    try_main(control_loop, None, None)
