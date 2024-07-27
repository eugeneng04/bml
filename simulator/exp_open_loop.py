import time
#from run_stm import *
import sim
import numpy as np
import scipy
import slider
import argparse
import utils_file

def genPattern():
    path = np.array([[0, 25, 48,  60], [0, -20, 0, -20]]) # input some points to do extrapolation on

    y_quadratic = scipy.interpolate.interp1d(path[0], path[1], kind = "quadratic", fill_value="extrapolate")

    new_path = sim.generateExtendedPath(path, y_quadratic, 60, 0, 100)
    robot_array = sim.gen_robot_array(15, 4)
    pattern, offsetArr = sim.pathFollow(new_path, y_quadratic, robot_array, inc = 0.2, plot = True)
    
    return pattern, offsetArr

def control_slider(offsetArr):
    for d in offsetArr:
        slider.moveDistance(d)

# def control_loop(q_output, result_folder, pattern): 
#     global regulator_vals, solenoid_vals
#     global charStart
#     i = 0
#     state = StateStruct()
#     print('control_loop- waiting for STM32READY\n')
#     time.sleep(1)    # check periodically for start    
#     while controlStop.is_set():
#         time.sleep(1)    # check periodically for start    
#     makeCmd('PRNWAIT', 1000)   # set wait time for state update in ms
#     time.sleep(3)
#     print('control_loop: started thread')
#     time_per_step = 4
    
#     regulator_vals =  np.array([0, 0, 0, 0, 0, 0, 0, 0])*1.
#     makePressureCmd()


#     while (not controlStop.is_set()):
#         if not stateQ.empty():
#             if not charStart.is_set():
#                 makePressureCmd()
#                 time.sleep(1)  # should run at state update rate                
#             else:
#                 print("characterization starts")
#                 for i in range(100):
#                     print('trial', i)
#                     # print("setting backbone to " +str(backbone_pressure)+ " PSI)")
#                     for j, r_val in enumerate(pattern):
#                         # print("setting actuator to " +str(actuator_pressure)+ " PSI)")
#                         state = stateQ.get()
#                         regulator_vals = r_val
#                         print(f'step {j}', pattern)

#                         makePressureCmd()
#                         for i, val in enumerate(regulator_vals):
#                             dumpQ(q_output, 'regulator', 'PWM{}'.format(i+1), val, time.time()-t0)
#                         time.sleep(time_per_step)
#                         if controlStop.is_set():
#                             break
#                     dumpQ(q_output, 'info', 'CYCLE_DONE', i, time.time()-t0)
#                     if controlStop.is_set():
#                         break
#                 charStart.clear()
#                 q_output_list = []
#                 while not q_output.empty():
#                     q_output_list.append(q_output.get())

#                 with open(os.path.join(result_folder, "queue.pickle"), "wb") as f:
#                     pickle.dump(q_output_list, f)
#                 print('queue saved')
#                 controlStop.set() # stop program after done characterization
#         else:
# #            print('stateQ empty')
#             # print("waiting for characterization start")
#             time.sleep(1)

#     print('control_loop: finished thread')
    
#     cameraStop.set()

if __name__ == '__main__':
    # aruco_detector.start_video(result_folder)

    # q_output = queue.Queue()
    # try_main(control_loop, q_output, result_folder)

    # pattern, offsetArr = genPattern()
    # print(offsetArr)
    # for i in offsetArr:
    #     slider.moveDistance(i)
    #     print(f"moved distance to {i}")
        
    #control_slider(offsetArr)
    
    parser = argparse.ArgumentParser()

    parser.add_argument("name", help = "folder for name of file")
    parser.add_argument("--dump", action="store_false", help = "whether to use saved output")
    folder_name = f"{utils_file.getCurrPath()}/logs/{parser.parse_args().name}"

    flag = utils_file.validData(folder_name, "pattern")

    if (parser.parse_args().dump or not flag):
        utils_file.createLogFolder(parser.parse_args().name)
        pattern, offsetArr = genPattern()


        if utils_file.isPath(f"{folder_name}/data.pickle"):
            saved_data = utils_file.openFile(folder_name)

            saved_data["pattern"] = pattern
            saved_data["offsetArr"] = offsetArr

            utils_file.saveFile(folder_name, saved_data)
            
        else:
            data = {"pattern": pattern, "offsetArr": offsetArr}
            utils_file.saveFile(folder_name, data)

    else:
        print("Using Saved Data")
        saved_data = utils_file.openFile(folder_name)
        pattern = saved_data["pattern"]
        offsetArr = saved_data["offsetArr"]

    print(pattern, offsetArr)
    for d in offsetArr:
        print(d)
        slider.moveDistance(d)