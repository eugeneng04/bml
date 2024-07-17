import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

fig, ax = plt.subplots() 

path = np.array([[0, 1, 2, 3 ,4],[0, 1, 2, 3, 4]]) # x, y


def plotPath(path):
    plt.scatter(path[0], path[1], color = "blue", label = "desired path")
    plt.legend
 
def rotate_robot(rot, len): #array of rotation
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
    plot = ax.plot(coords[0], coords[1], '--bo', label='robot', linewidth=1, alpha=0.5)
    return plot

global global_pos
global_pos = 0

def move_up(coords, offset):
    global global_pos
    global_pos = global_pos + offset
    return (coords[0], coords[1] + global_pos)

def rotations_to_rad(rotations):
    return (rotations* np.pi)/180

def gen_len_array(len, num):
    return np.ones(num) * len

if __name__ == "__main__":
    plotPath(path)
    #plt.show()
    len = gen_len_array(1, 3)
    rotations1 = rotations_to_rad(np.array([0, 0, 0]))
    rotations2 = rotations_to_rad(np.array([30, 0, 0]))
    rotations3 = rotations_to_rad(np.array([30, 60, 0]))
    rotations4 = rotations_to_rad(np.array([30, 60, -30]))
    #H = rotate_robot(rotations, lens)
    H1 = plot_robot(get_pos(rotate_robot(rotations1, len)))
    H2 = plot_robot(move_up(get_pos(rotate_robot(rotations2, len)), 0.5))
    H3 = plot_robot(move_up(get_pos(rotate_robot(rotations3, len)), 0.5))
    H4 = plot_robot(move_up(get_pos(rotate_robot(rotations4, len)), 0.5))
    total = [H1, H2, H3, H4]
    #print(H)
    #print(get_pos(H))
    #plot_robot(get_pos(H))
    ani = animation.ArtistAnimation(fig=fig, artists=total, interval=500)
    plt.show()