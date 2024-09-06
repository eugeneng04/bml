import time
from run_stm_12 import *

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
                time.sleep(1)  # should run at state update rate                
            else:
                print("starting stepper test")
                makeCmd('PFRQ1', 8000)
                time.sleep(5)
                makeCmd('PFRQ1', 0)
                if controlStop.is_set():
                    break
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
    print(args.run_name)
    if is_camera_available:
        aruco_detector.start_video(result_folder)

    q_output = queue.Queue()
    # try_main(control_loop, q_output, result_folder)
    try_main(control_loop, None, None)
