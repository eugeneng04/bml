import time
from run_stm_12 import *
import sim
import numpy as np
import scipy
import argparse
import utils_file
import matplotlib.pyplot as plt
import controller
import angles
import stepper

def genPattern(new_path, y_quadratic):
    robot_array = sim.gen_robot_array(15, 4)
    pattern, offsetArr, robotArr, rotArr = sim.pathFollow(new_path, y_quadratic, robot_array, inc = 0.2, plot = True)
    
    return pattern, offsetArr, robotArr, rotArr

def control_loop(q_output, result_folder, pattern): 
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
    time_per_step = 4
    
    regulator_vals =  np.array([0, 0, 0, 0, 0, 0, 0, 0])*1.
    makePressureCmd()

    pid_controller1 = controller.pid_controller(1, 0.5, 2, 0) #index, Kp, Ki
    pid_controller2 = controller.pid_controller(2, 0.5, 2, 0) #index, Kp, Ki
    pid_controller3 = controller.pid_controller(3, 0.5, 2, 0) #index, Kp, Ki
    pid_controller4 = controller.pid_controller(4, 0.5, 2, 0) #index, Kp, Ki

    controllers = [pid_controller1, pid_controller2, pid_controller3, pid_controller4]


    while (not controlStop.is_set()):
        if not stateQ.empty():
            if not charStart.is_set():
                makePressureCmd()
                time.sleep(1)  # should run at state update rate                
            else:
                print("characterization starts")
                frameQ = queue.Queue()
                outputQ = queue.Queue()
                scale = []
                angle_thread = threading.Thread(target = angles.angle_loop, args = ((frameQ, outputQ, scale), ))
                for j, angle in enumerate(pattern):
                    if scale is not None:
                        pxl_scale = scale
                    regulator_vals = np.zeros(12)
                    for a in angle:
                        controllers[i].set_target(a)
                    stepper.move_stepper_distance(offsetArr[j])
                    while not any([controller.exit for controller in controllers]) and not controlStop.is_set():
                        angles = angle_thread.get()
                        for i in range(len(angles)):
                            actual_angle = angles[i]
                            print(f"actual angle: {actual_angle}")
                            regulator_vals += controllers[i].convert(controllers[i].compute(actual_angle))
                        
                        makePressureCmd_new(regulator_vals)
                        
                        print(regulator_vals)
                    #slider.moveDistance(offsetArr[j]) # move slider set distance
                    
                    time.sleep(1)
                    if controlStop.is_set():
                        break
            
                    if controlStop.is_set():
                        break
                charStart.clear()
                controlStop.set() # stop program after done characterization
        else:
            time.sleep(1)

    print('control_loop: finished thread')
    
    cameraStop.set()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()

    parser.add_argument("name", help = "folder for name of file")
    parser.add_argument("--dump", action="store_false", help = "whether to use saved output")
    folder_name = f"{utils_file.getCurrPath()}/logs/{parser.parse_args().name}"

    flag = utils_file.validData(folder_name, "pattern")

    if (parser.parse_args().dump or not flag):
        utils_file.createLogFolder(parser.parse_args().name)
        path = np.array([[0, 25, 48,  60], [0, -20, 0, -20]]) # input some points to do extrapolation on

        y_quadratic = scipy.interpolate.interp1d(path[0], path[1], kind = "quadratic", fill_value="extrapolate")

        new_path = sim.generateExtendedPath(path, y_quadratic, 60, 0, 100)
        pattern, offsetArr, robotArr, rotArr = genPattern(new_path, y_quadratic)


        if utils_file.isPath(f"{folder_name}/data.pickle"):
            saved_data = utils_file.openFile(folder_name)

            saved_data["pattern"] = pattern
            saved_data["offsetArr"] = offsetArr
            saved_data["robotArr"] = robotArr
            saved_data["rotArr"] = rotArr

            utils_file.saveFile(folder_name, saved_data)
            
        else:
            data = {"pattern": pattern, "offsetArr": offsetArr, "robotArr": robotArr, "rotArr": rotArr}
            utils_file.saveFile(folder_name, data)

    else:
        print("Using Saved Data")
        saved_data = utils_file.openFile(folder_name)
        pattern = saved_data["pattern"]
        offsetArr = saved_data["offsetArr"]
        robotArr = saved_data["robotArr"]
        rotArr = saved_data["rotArr"]

    #print(pattern, offsetArr)
    # for d in offsetArr:
    #     print(d)
    #     slider.moveDistance(d)
    # try_main(control_loop, None, None)
    path = np.array([[0, 25, 48,  60], [0, -20, 0, -20]]) # input some points to do extrapolation on

    y_quadratic = scipy.interpolate.interp1d(path[0], path[1], kind = "quadratic", fill_value="extrapolate")

    new_path = sim.generateExtendedPath(path, y_quadratic, 60, 0, 100)
    sim.plotPath(new_path, "desired path", "green")
    plt.xlim(0,np.max(new_path[0]) + 10)
    plt.ylim(-(np.max(new_path[0]) + 10)/2, (np.max(new_path[0]) + 10)/2)
    plt.show(block = False)
    for i in range(len(robotArr)):
        if i % 10 == 0:
            plotted_robot = sim.plot_robot(robotArr[i])
            print(pattern[i])
            print(rotArr[i])
            plt.draw()
            input("input any char to view next: ")
            plotted_robot.remove()
