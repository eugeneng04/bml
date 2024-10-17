import time
from run_stm_12 import *
import cv2
from video import *
import multiprocessing

steps_per_revolution = 200 * 32
pitch = 1 #1mm pitch, 1mm per revolution
frequency = 3000

camera_id = 1
cap = cv2.VideoCapture(camera_id)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)

def move_stepper_distance(distance, steps_per_revolution = steps_per_revolution, pitch = pitch, frequency = frequency):
    steps_required = int((distance / pitch) * steps_per_revolution)
    time_to_run = abs(steps_required / frequency)
    if distance > 0:
        makeCmd('PFRQ1', frequency)
    else:
        makeCmd("PFRQ1", -1 * frequency)
    time.sleep(time_to_run)
    makeCmd("PFRQ1", 0)

q = queue.Queue()
kp = 500
def control_loop(q_output, result_folder): 
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
    while (not controlStop.is_set()):
        if not stateQ.empty():
            if not charStart.is_set():
                # user_input = input("enter distance: ")
                # move_stepper_distance(float(user_input))
                if controlStop.is_set():
                    break     
                time.sleep(1)  # should run at state update rate 
            else:
                print("starting stepper test")
                first_frame = True
                while (not controlStop.is_set()):
                    base_tag = 2
                    slider_tag = 17
                    moving_tag = 10

                    ret, frame = cap.read()
                    if not ret:
                        break

                    corners, ids, c = detect_aruco_tag(frame)

                    #print(corners, ids)
                    if ids is not None: 
                        if first_frame and (2 in ids): # get the scale
                            base_index = np.where(ids == base_tag)[0][0]
                            h, w, *_ = frame.shape
                            scale = pixelToMM(corners[base_index], 4.5) # change size of artag here
                            print(scale)
                            first_frame = False

                    if ids is not None:
                        if moving_tag in ids and slider_tag in ids:
                            moving_index = np.where(ids == moving_tag)[0][0]
                            slider_index = np.where(ids == slider_tag)[0][0]

                            moving_coords = corners[moving_index]
                            slider_coords = corners[slider_index]
                            distance = ((moving_coords - slider_coords) * scale)[0][0][0]
                            print(f"moving distance: {distance}")
                            #move_stepper_distance(float(-distance))
                            if distance > 0:
                                cmd = -min(3000, distance * kp)
                            else:
                                cmd =  -max(-3000, distance * kp)
                            print(cmd)
                            makeCmd('PFRQ1', cmd)
                    if controlStop.is_set():
                        break

                    # cv2.imshow("image", frame)
                    # key = cv2.waitKey(1)
                    # if key == ord("q"):
                    #     quit_early = True
                    #     break
                charStart.clear()
                controlStop.set()
        else:
            time.sleep(1)

    print('finished thread')
    
    cameraStop.set()

if __name__ == '__main__':
    import argparse
    import json
    import os
    import utils
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default='./data-raw')
    parser.add_argument("--run_name", default='test')
    parser.add_argument('--comment', default="")
    parser.add_argument("--debug", action='store_true')

    args = parser.parse_args()
    #args.run_name = os.path.splitext(os.path.basename(__file__))[0]
    result_folder = utils.create_runs_folder(args)
    #print(args.run_name)
    if is_camera_available:
        aruco_detector.start_video(result_folder)

    q_output = queue.Queue()
    # try_main(control_loop, q_output, result_folder)
    try_main(control_loop, None, None)
    # while True:
    #     pass
    # video_thread()
