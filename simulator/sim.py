import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from scipy.optimize import minimize
import scipy.interpolate

fig, ax = plt.subplots() 

#path = np.array([[0, 1, 2, 3 ,4],[0, 1, 2, 3, 4]]) # x, y


def plotPath(path):
    plt.plot(path[0], path[1], color = "black", label = "desired path")
    plt.legend
 
def rotate_robot(rot, len): #array of rotation
    #print(len)
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
        #transformations.append(H)
        H = H @ Htrans
        transformations.append(H)
    return transformations

def get_pos(H):
    x_coords = []
    y_coords = []
    
    for h in H:
        # Extract the x and y from the transformation matrix
        x_coords.append(h[0, 2])
        y_coords.append(h[1, 2])
    
    return np.array(x_coords), np.array(y_coords)

def plot_robot(coords):
    plot = plt.plot(coords[0], coords[1], '--bo', label='robot', linewidth=1, alpha=0.5)
    return plot

def move_up(coords, offset):
    return (coords[0] + offset, coords[1])

def rotations_to_rad(rotations):
    return (rotations* np.pi)/180

def gen_len_array(len, num):
    return np.ones(num) * len

def objective(desired_pos, theta, len):
    theta_rad = rotations_to_rad(theta[:-1])
    H = rotate_robot(theta_rad, len)
    coords = get_pos(H)
    offset_coords = move_up(coords,theta[-1])
    #print(offset_coords)
    l2_norm = np.linalg.norm(desired_pos - offset_coords, 2)
    return l2_norm

def solve_optimal(len, current_pos, desired_pos):
    len_arr = gen_len_array(3, len)
    objective_func = lambda theta: objective(desired_pos, theta, len_arr)
    sol = minimize(objective_func, current_pos)
    return sol.x

def calculate_distances(coordinates):
    x_coords = coordinates[0]
    y_coords = coordinates[1]
    
    num_points = len(x_coords)
    distances = np.zeros(num_points - 1)
    
    for i in range(num_points - 1):
        distances[i] = np.sqrt((x_coords[i+1] - x_coords[i])**2 + (y_coords[i+1] - y_coords[i])**2)
    
    return distances


if __name__ == "__main__":
    path = np.array([[0, 8, 12, 16, 20], [0, 0, 1.5, -1.5, 1.5]])
    # plt.scatter(path[0], path[1], color = "red", label = "user input")
    x_interp = np.linspace(np.min(path[0]), np.max(path[0]), 100)

    y_quadratic = scipy.interpolate.interp1d(path[0], path[1], kind = "quadratic")
    new_path = [x_interp, y_quadratic(x_interp)]
    # plotPath(new_path)
    # plt.legend()
    # plt.show()
    #print(new_path)

    
    robot_coords = np.array([[0, 3, 6, 9, 12],[0, 0, 0, 0, 0]])
    init_conds = [0, 0, 0, 0 ,0]
    prev_optimal = init_conds
    for i in range(200):
        plotPath(new_path)
        #test_path = np.array([new_path[0][i:i+5], new_path[1][i:i+5]])
        adjusted_x = robot_coords[0]+0.1
        next_coords = np.array([adjusted_x, y_quadratic(adjusted_x)])
        plt.scatter(next_coords[0], next_coords[1], color = "red")
        optimal_params = solve_optimal(4, prev_optimal, next_coords)
        prev_optimal = optimal_params
        rot = optimal_params[:-1]
        offset = optimal_params[-1]
        robot_coords = move_up(get_pos(rotate_robot(rotations_to_rad(rot), gen_len_array(3, 4))), offset)
        plot_robot(robot_coords)
        #print(calculate_distances(robot_coords))
        plt.xlim(0,25)
        plt.ylim(-12.5, 12.5)
        plt.draw()
        plt.pause(0.001)
        plt.clf()
