import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import scipy.optimize
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

def con1(theta): #angle constraints
    lower_bound = -85 # Example lower bound
    upper_bound = 85  # Example upper bound
    return [theta[i] - lower_bound for i in range(len(theta) - 1)] + [upper_bound - theta[i] for i in range(len(theta) - 1)]

def con2(theta):
    global prev_optimal
    return theta[-1] - (prev_optimal[-1])

def con3(theta):
    return theta[-1] - 0.3

def solve_optimal(len, current_pos, desired_pos):
    len_arr = gen_len_array(15, len) # edit length of robot here
    objective_func = lambda theta: objective(desired_pos, theta, len_arr)
    sol = scipy.optimize.minimize(objective_func, current_pos, method = "SLSQP", constraints=[{'type': 'ineq', 'fun': con1},
                                                             {'type': 'ineq', 'fun': con2}, {"type": "ineq", "fun": con3}], options={'tol': 1})
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
    global prev_optimal
    #upper_bound = np.array([[0, 25, 48,  60], [12, -24.5 + 12, 12, -24.5 + 12]])
    path = np.array([[0, 25, 48,  60], [0, -15, 0, -15]])
    # plt.scatter(path[0], path[1], color = "red", label = "user input")
    x_interp = np.linspace(np.min(path[0]), np.max(path[0]) + 60, 100)
    #y_quadratic_upper = scipy.interpolate.interp1d(upper_bound[0], upper_bound[1], kind = "quadratic", fill_value="extrapolate")
    y_quadratic = scipy.interpolate.interp1d(path[0], path[1], kind = "quadratic", fill_value="extrapolate")
    def y_quadratic_offset(robot_len, x, straight, func):
        return_arr = []
        for x_i in x:
            if x_i < robot_len - 0.2:
                return_arr.append(straight)
            else:
                return_arr.append(func(x_i - robot_len))
        return return_arr
    #new_upper_bound = [x_interp, y_quadratic_offset(60, x_interp, 10, y_quadratic_upper)]
    #new_lower_bound = [new_upper_bound[0], new_upper_bound[1] - np.ones(len(new_upper_bound[1])) * 18]
    new_path = [x_interp, y_quadratic_offset(60, x_interp, 0, y_quadratic)]
    robot_coords = np.array([[0, 15, 30, 45, 60],[0, 0, 0, 0, 0]])
    init_conds = [0, 0, 0, 0 ,0]
    prev_optimal = init_conds
    while np.max(robot_coords[0]) < np.max(x_interp):
        plotPath(new_path)
        plotPath([new_path[0], new_path[1] - np.ones(len(new_path[1])) * 10])
        plotPath([new_path[0], new_path[1] + np.ones(len(new_path[1])) * 10])
        #test_path = np.array([new_path[0][i:i+5], new_path[1][i:i+5]])
        adjusted_x = robot_coords[0]+0.1
        next_coords = np.array([adjusted_x, y_quadratic_offset(60, adjusted_x, 0, y_quadratic)])
        plt.scatter(next_coords[0], next_coords[1], color = "red")
        optimal_params = solve_optimal(4, prev_optimal, next_coords)
        prev_optimal = optimal_params
        rot = optimal_params[:-1]
        print(rot)
        offset = optimal_params[-1]
        robot_coords = move_up(get_pos(rotate_robot(rotations_to_rad(rot), gen_len_array(15, 4))), offset) # edit length of robot here
        plot_robot(robot_coords)
        #print(calculate_distances(robot_coords))
        plt.xlim(0,140)
        plt.ylim(-70, 70)
        plt.draw()
        plt.pause(0.001)
        plt.clf()
    plotPath(new_path)
    plotPath([new_path[0], new_path[1] - np.ones(len(new_path[1])) * 10])
    plotPath([new_path[0], new_path[1] + np.ones(len(new_path[1])) * 10])
    plt.scatter(next_coords[0], next_coords[1], color = "red")
    plot_robot(robot_coords)
    plt.xlim(0,140)
    plt.ylim(-70, 70)
    plt.show()
    
