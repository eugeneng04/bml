import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import scipy.interpolate
import robot_characterization
from datetime import datetime


fig, ax = plt.subplots() 

def plotPath(path, name, color = "black"):
    plt.plot(path[0], path[1], color = color, label = name)
    plt.legend()

def rotate_robot(rot, len): # takes in array of angles to rotate and array corresponding to length of robot, returns array of state matrices of every joint
    H = np.eye(3)
    transformations = [H]
    for i in range(rot.size):
        Hrot = np.array([[np.cos(rot[i]), -np.sin(rot[i]), 0],
                        [np.sin(rot[i]), np.cos(rot[i]), 0],
                        [0, 0, 1]])
        Htrans = np.array([[1, 0, len[i]],
                          [0, 1, 0],
                          [0, 0, 1]])
        H = H @ Hrot
        H = H @ Htrans
        transformations.append(H)

    return transformations

def get_pos(H): # takes in transformations, outputs array of the positions of every joint
    x_coords = []
    y_coords = []
    
    for h in H:
        # Extract the x and y from the transformation matrix
        x_coords.append(h[0, 2])
        y_coords.append(h[1, 2])
    
    return np.array(x_coords), np.array(y_coords)

def plot_robot(coords): # plots robot given coordinates from get_pos
    plot, = plt.plot(coords[0], coords[1], '--bo', label='robot', linewidth=1, alpha=0.5)
    return plot

def move_up(coords, offset): # offset coordinates because of linear stage
    return (coords[0] + offset, coords[1])

def rotations_to_rad(rotations): # conversion from degrees to radians
    return (rotations* np.pi)/180

def gen_robot_array(len, num): # generate robot array for length of robot with uniform lengths
    return np.ones(num) * len

global robot_coords
robot_coords = None

def objective(desired_pos, params, len, offset): # objective function for optimization solver 
    theta_rad = rotations_to_rad(params)
    H = rotate_robot(theta_rad, len)
    coords = get_pos(H)
    #offset_coords = move_up(coords,params[-1])
    offset_coords = move_up(coords, offset)
    robot_coords = offset_coords
    l2_norm = np.linalg.norm(desired_pos - offset_coords, 2)
    return l2_norm

def con1(params, lower_bound_arr, upper_bound_arr): #angle constraints
    # lower_bound = -50 # Example lower bound
    # upper_bound = 50  # Example upper bound
    return [params[i] - lower_bound_arr[i] for i in range(len(params))] + [upper_bound_arr[i] - params[i] for i in range(len(params))]

def con2(params, prev_optimal):
    return params - prev_optimal - 10

def con3(params, top_func, bottom_func):
    global robot_coords
    x_vals = robot_coords[0]
    y_vals = robot_coords[1]
    return np.hstack([top_func(x_vals) - y_vals, y_vals - bottom_func(x_vals)])

def solve_optimal(robot_arr, current_pos, desired_pos, prev_optimal, lower_bound, upper_bound, offset, top_func, bottom_func):
    objective_func = lambda params: objective(desired_pos, params, robot_arr, offset)
    # sol = scipy.optimize.minimize(objective_func, current_pos, method = "SLSQP", constraints= [{'type': 'ineq', 'fun': lambda params: con1(params, lower_bound, upper_bound)},
    #                                                                                             {'type': 'ineq', 'fun': lambda params: con2(params, prev_optimal)}])

    sol = scipy.optimize.minimize(objective_func, current_pos, method = "SLSQP", constraints= [{'type': 'ineq', 'fun': lambda params: con1(params, lower_bound, upper_bound)},
                                                                                               {'type': 'ineq', 'fun': lambda params: con3(params, top_func, bottom_func)}])
    return sol.x

def calculate_distances(coordinates):
    x_coords = coordinates[0]
    y_coords = coordinates[1]
    
    num_points = len(x_coords)
    distances = np.zeros(num_points - 1)
    
    for i in range(num_points - 1):
        distances[i] = np.sqrt((x_coords[i+1] - x_coords[i])**2 + (y_coords[i+1] - y_coords[i])**2)
    
    return distances

def y_quadratic_offset(robot_len, x, straight, func):
        return_arr = []
        for x_i in x:
            if x_i < robot_len - 0.2:
                return_arr.append(straight)
            else:
                return_arr.append(func(x_i - robot_len))
        return return_arr

def generateExtendedPath(path, y_func,  offset, straight, iters = 100): 
    # generates extended path because of initial offset for the robot
    # path is a set of points we want to follow
    # y func is function that will determine our y-values
    # offset is how far forwards we should set it to be 
    # straight is the default y value we want for our straight section
    # returns array of x and y values for our new modified path

    x_interp = np.linspace(np.min(path[0]), np.max(path[0]) + offset, iters)
    new_path = [x_interp, y_quadratic_offset(offset, x_interp, straight, y_func)]
    return new_path

def pathFollow(path, y_quadratic, robot_array, vel = 0.5, plot = True, ):
    pattern = []
    offsetArr = []
    robotArr = []
    rotArr = []
    robot_coords = np.array([np.zeros(len(robot_array) + 1),np.zeros(len(robot_array) + 1)])
    init_conds = np.zeros(len(robot_array))
    # robot_array = gen_robot_array(15, 4)
    prev_optimal = init_conds
    prev_t = datetime.now()
    delta_t = None
    total_inc = 0

    yTop, yBot = genRotationToPressureFunc()


    if plot:
        plotPath(path, "desired path", "green")
        plotPath([path[0], path[1] - np.ones(len(path[1])) * 10], "lower bound")
        plotPath([path[0], path[1] + np.ones(len(path[1])) * 10], "upper bound")
        plt.xlim(0,np.max(path[0]) + 10)
        plt.ylim(-(np.max(path[0]) + 10)/2, (np.max(path[0]) + 10)/2)

    while np.max(robot_coords[0]) < np.max(path[0]):
        curr_t = datetime.now()
        delta_t = (curr_t - prev_t).total_seconds()
        inc = delta_t * vel
        total_inc += inc
        print(inc)

        adjusted_x = robot_coords[0] + inc

        next_coords = np.array([adjusted_x, y_quadratic_offset(60, adjusted_x, 0, y_quadratic)])

        optimal_params = solve_optimal(robot_array, prev_optimal, next_coords, prev_optimal, [-33, -55, -48, -49], [70, 70, 45, 35], total_inc, )

        #pattern_i, offset_i = convertParams(optimal_params, prev_optimal, yTop, yBot)

        pattern_i= convertParams_new(optimal_params)

        #q.append(optimal_params_converted)
        pattern.append(pattern_i)

        prev_optimal = optimal_params

        rot = optimal_params

        robot_coords = move_up(get_pos(rotate_robot(rotations_to_rad(rot), robot_array)), total_inc)
        robotArr.append(robot_coords)
        rotArr.append(rot)
        if plot:
    
            desired_coords = plt.scatter(next_coords[0], next_coords[1], color = "red")
            plotted_robot = plot_robot(robot_coords)
            #print(calculate_distances(robot_coords))
            plt.draw()
            plt.pause(0.001)
            plotted_robot.remove()
            desired_coords.remove()

        prev_t = curr_t

    if plot:
        print("press q to quit and save queue")
        plt.scatter(next_coords[0], next_coords[1], color = "red")
        plot_robot(robot_coords)
        plt.show()

    return pattern, offsetArr, robotArr, rotArr

def genRotationToPressureFunc(): #helper function that generates function, want to map angle input to kpi output
    topCurve = [[-45, -25, 0, 25, 65], [-172, -20, 22, 40, 172]]
    bottomCurve = [[-45, -25, 0, 25, 65], [-172, -75, -20, 0, 172]]
    x = np.linspace(-45, 65, 100)
    yTop = scipy.interpolate.interp1d(topCurve[0], topCurve[1], kind = "cubic")
    yBot = scipy.interpolate.interp1d(bottomCurve[0], bottomCurve[1], kind = "cubic")
    return yTop, yBot #assume yTop is when its left to right (increasing angle), yBot is right to left (decreasing)

def rotationToPressure(angle, func): # maps rotation to pressure, input is pressure angle, output is a [left, right] where right is positive, left is negative
    #increasing is 1 if going left to right, -1 is when going right to left
    kpiToPsi_factor = 0.145038
    if angle > 0:
        return [abs(func(angle) * kpiToPsi_factor), 0]
    return [0, abs(func(angle) * kpiToPsi_factor)]


def convertParams(params, prevParams, yTop, yBot): # convert our output of path follow to pressure input for run_stm, input is queue which is output of pathFollow
    rot = np.array(params)
    prevRot = np.array(prevParams)

    pressureArr = []

    #deltaRot = rot - prevRot
    for i in range(len(rot)):
        if rot[i] > 0: #increasing
            pressureIn = rotationToPressure(rot[i], yTop)
        else:
            pressureIn = rotationToPressure(rot[i], yBot)
        pressureArr += pressureIn

    return pressureArr

global characterized_act_top
global characterized_act_bot
#characterized_act = robot_characterization.get_functions()
import utils_file
folder_name = f"{utils_file.getCurrPath()}/Data"
saved_data = utils_file.openFile(folder_name)
characterized_act_top = [saved_data["top_function_1"], saved_data["top_function_2"], saved_data["top_function_3"], saved_data["top_function_4"]]
characterized_act_bot = [saved_data["bottom_function_1"], saved_data["bottom_function_2"], saved_data["bottom_function_3"], saved_data["bottom_function_4"]]

def convertParams_new(params):
    global characterized_act # odd goes left, even goes right, 1 indexed
    pressureArr = []
    rot = params

    for i in range(len(rot)): # positive will be left, negative right
        #print(i)
        if rot[i] > 0:
            pressureArr += [characterized_act_top[i](abs(rot[i])), 0]
        else:
            #print(2*i)
            pressureArr += [0, characterized_act_bot[i](abs(rot[i]))]
        
    return pressureArr

if __name__ == "__main__":
    path = np.array([[0, 25, 48,  60], [0, -20, 0, -20]]) # input some points to do extrapolation on

    y_quadratic = scipy.interpolate.interp1d(path[0], path[1], kind = "quadratic", fill_value="extrapolate")

    plt.axhline(y = 0, linestyle = "dashed", color = "orange", label = "linear slider")
    plt.legend()
    new_path = generateExtendedPath(path, y_quadratic, 60, 0, 100)
    robot_array = gen_robot_array(15, 4)
    pattern, offsetArr, robotArr, rotArr = pathFollow(new_path, y_quadratic, robot_array, vel = 5, plot = True)
    print(pattern)

    #print(offsetArr)

    # x = np.linspace(-45, 65, 100)
    # yTop, yBot = genRotationToPressureFunc()
    # topCurve = [yTop(x), x]
    # botCurve = [yBot(x), x]
    # plotPath(topCurve, "top", "red")
    # plotPath(botCurve, "bot", "blue")
    # plt.ylabel("angle (deg)")
    # plt.xlabel("pressure (kpi)")
    # plt.ylim(-100,100)
    # plt.show()
    
