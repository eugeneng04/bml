import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import scipy.optimize
import scipy.interpolate
from collections import deque

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

def objective(desired_pos, params, len): # objective function for optimization solver 
    theta_rad = rotations_to_rad(params[:-1])
    H = rotate_robot(theta_rad, len)
    coords = get_pos(H)
    offset_coords = move_up(coords,params[-1])
    l2_norm = np.linalg.norm(desired_pos - offset_coords, 2)
    return l2_norm

def con1(params, lower_bound, upper_bound): #angle constraints
    # lower_bound = -50 # Example lower bound
    # upper_bound = 50  # Example upper bound
    return [params[i] - lower_bound for i in range(len(params) - 1)] + [upper_bound - params[i] for i in range(len(params) - 1)]

def con2(params, prev_optimal):
    return params[-1] - (prev_optimal[-1]) - 0.1

def solve_optimal(robot_arr, current_pos, desired_pos, prev_optimal, lower_bound, upper_bound):
    objective_func = lambda params: objective(desired_pos, params, robot_arr)
    sol = scipy.optimize.minimize(objective_func, current_pos, method = "SLSQP", constraints= [{'type': 'ineq', 'fun': lambda params: con1(params, lower_bound, upper_bound)},
                                                                                                {'type': 'ineq', 'fun': lambda params: con2(params, prev_optimal)}])
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

def pathFollow(path, y_quadratic, robot_array, inc = 0.1, plot = True):
    q = deque()
    robot_coords = np.array([np.zeros(len(robot_array) + 1),np.zeros(len(robot_array) + 1)])
    init_conds = np.zeros(len(robot_array) + 1)
    # robot_array = gen_robot_array(15, 4)
    prev_optimal = init_conds

    if plot:
        plotPath(new_path, "desired path", "green")
        plotPath([new_path[0], new_path[1] - np.ones(len(new_path[1])) * 10], "lower bound")
        plotPath([new_path[0], new_path[1] + np.ones(len(new_path[1])) * 10], "upper bound")
        plt.xlim(0,np.max(path[0]) + 10)
        plt.ylim(-(np.max(path[0]) + 10)/2, (np.max(path[0]) + 10)/2)

    while np.max(robot_coords[0]) < np.max(new_path[0]):

        adjusted_x = robot_coords[0] + inc

        next_coords = np.array([adjusted_x, y_quadratic_offset(60, adjusted_x, 0, y_quadratic)])


        optimal_params = solve_optimal(robot_array, prev_optimal, next_coords, prev_optimal, -50, 50)

        q.append(optimal_params)

        prev_optimal = optimal_params

        rot = optimal_params[:-1]

        offset = optimal_params[-1]

        robot_coords = move_up(get_pos(rotate_robot(rotations_to_rad(rot), robot_array)), offset)

        if plot:
    
            desired_coords = plt.scatter(next_coords[0], next_coords[1], color = "red")
            plotted_robot = plot_robot(robot_coords)
            #print(calculate_distances(robot_coords))
            plt.draw()
            plt.pause(0.001)
            plotted_robot.remove()
            desired_coords.remove()
    
    if plot:
        print("press q to quit and save queue")
        plt.scatter(next_coords[0], next_coords[1], color = "red")
        plot_robot(robot_coords)
        plt.show()

    return q

if __name__ == "__main__":
    path = np.array([[0, 25, 48,  60], [0, -20, 0, -20]]) # input some points to do extrapolation on

    y_quadratic = scipy.interpolate.interp1d(path[0], path[1], kind = "quadratic", fill_value="extrapolate")

    new_path = generateExtendedPath(path, y_quadratic, 60, 0, 100)
    robot_array = gen_robot_array(15, 4)
    q = pathFollow(new_path, y_quadratic, robot_array, inc = 0.2, plot = False)
    print(q)
    
