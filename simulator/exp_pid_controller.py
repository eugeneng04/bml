import time
import numpy as np
from run_stm_12 import *
import argparse
import utils_file
import characterization
import controller

def control_loop(q_output, result_folder): 
    characterizationThread = threading.Thread(group = None, target = characterization.calcAngle, name="angleThread")
    characterizationThread.daemon = False

    #characterizationThread.start() # uncomment this to view angles

    frameThread = threading.Thread(group = None, target = characterization.cameraThread, name="frameThread")
    frameThread.daemon = False

    frameThread.start() # uncomment this to view angles

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
    time_per_step = 1

    pid_controller = controller.pid_controller(1, 0.5, 2, 0) #index, Kp, Ki
    targets = [30, 15, 0, -15, -30]

    while (not controlStop.is_set()):
        if not stateQ.empty():
            if not charStart.is_set():
                makePressureCmd()
                time.sleep(1)  # should run at state update rate                
            else:
                print("characterization starts")
                global regulator_vals
                for target in targets:
                    pid_controller.set_target(target)
                    while pid_controller.exit == False and not controlStop.is_set():
                        angles = characterization.calcAngleLive()
                        if len(angles) == 4:
                            actual_angle = angles[1]
                            print(f"actual angle: {actual_angle}")
                            regulator_vals = pid_controller.convert(pid_controller.compute(actual_angle))
                            makePressureCmd_new(regulator_vals)
                            print(regulator_vals)
                        time.sleep(time_per_step)
                        if controlStop.is_set():
                            break
                    print(f"reached target! actual angle: {actual_angle}")
                    time.sleep(3)
                    if controlStop.is_set():
                        break
                if controlStop.is_set():
                    break
                
                
                charStart.clear()
                controlStop.set() # stop program after done characterization
                characterization.frameStop.set()
                
        else:
#            print('stateQ empty')
            # print("waiting for characterization start")
            time.sleep(1)

    print('control_loop: finished thread')
    print("saving data")
    characterization.frameStop.set()

if __name__ == '__main__':
    import argparse
    import json
    import os
    # parser = argparse.ArgumentParser()

    # parser.add_argument("name", help = "folder for name of file")
    # parser.add_argument("--dump", action="store_false", help = "whether to use saved output")
    # utils_file.createLogFolder(parser.parse_args().name)
    # folder_name = f"{utils_file.getCurrPath()}/logs/{parser.parse_args().name}"
    
    # flag = utils_file.validData(folder_name, "pattern")

    # for i in range(4): # 4 actuators
    #     for j in range(1): #we want to do this 1 times
    #         for k in range(2):
    #             pattern_arr = [0, 5, 10, 15, 20, 25, 30, 35]
    #             for val in pattern_arr:
    #                 regulator_vals = np.zeros(12)

    #                 regulator_vals[2*i + k] = val
    #                 print(regulator_vals)
    try_main(control_loop, None, None)

