# we want to figure out the level of noise: fixed camera and fixed ARTag, use cv2 program to get 4 corners of ARTag and average those values to get the center
# graph the center over time to see how much it changes

#only scale on first frame to speed up process -> map pixels to size of ARTag (dimensions)

import cv2
import cv2.aruco as aruco
import numpy as np
import matplotlib.pyplot as plt

import utils_file
import argparse

def detect_aruco_tag(frame):
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    # dictionary = aruco.extendDictionary(30, 3)

    # dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
    parameters =  aruco.DetectorParameters()
    # parameters.polygonalApproxAccuracyRate=0.05
    detector = aruco.ArucoDetector(dictionary, parameters)
    return detector.detectMarkers(frame)

#assume only 1 ARTag
def get_rotation_from_corners(corners):
    # Reshape corners into a 2D array
    corners = np.array(corners).reshape(-1, 2)
    centroid = np.mean(corners, axis=0)

    # Compute vectors from centroid to each corner
    dx = corners[1][0] - corners[0][0]
    dy = corners[1][1] - corners[0][1]
    rotation_rad = np.arctan2(dy, dx)
    rotation_deg = np.degrees(rotation_rad)

    return centroid, rotation_deg


def pixelToMM(corners, mm):
    corners = np.array(corners).reshape(-1, 2)
    #top line
    top = np.linalg.norm(corners[0] - corners[1])
    #bottom line
    bottom = np.linalg.norm(corners[2] - corners[3])

    #if tilted then top line and bottom line are different sized
    avg_len = np.mean((top, bottom))
    return mm/avg_len

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("name", help = "folder for name of file")
    parser.add_argument("--dump", action="store_false", help = "whether to use saved output")
    folder_name = f"{utils_file.getCurrPath()}/logs/{parser.parse_args().name}"

    flag = utils_file.validData(folder_name, "x_coords")

    quit_early = False

    if (parser.parse_args().dump or not flag):
        print("Parsing Video in Real Time")
        cap = cv2.VideoCapture(f"{folder_name}/video.avi")
        frames = []
        cornerLst = []
        idsLst = []

        dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        parameters =  aruco.DetectorParameters()
        detector = aruco.ArucoDetector(dictionary, parameters)
        aruco_detector = detector.detectMarkers #function that takes in a frame

        first_frame = True
        scale = 0
        x_coords = []
        y_coords = []
        rotation = []
        fig, ax = plt.subplots()

        brightness = 1
        contrast = 1
        while True:
            ret, frame = cap.read()
            frames.append(frame)
            if not ret:
                break

            # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            # frame = cv2.resize(frame, (640, 640))
            # #frame = cv2.GaussianBlur(frame, (1,1), 0)
            # frame = cv2.addWeighted(frame, contrast, np.zeros(frame.shape, frame.dtype), 0, brightness) 
            # kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) 
            
            # # Sharpen the image 
            # frame = cv2.filter2D(frame, -1, kernel) 
            corners, ids, c = detect_aruco_tag(frame)
            cornerLst.append(corners)
            idsLst.append(ids)
            if ids is not None:
                if first_frame:
                    h, w, *_ = frame.shape
                    scale = pixelToMM(corners[0], 3)
                    first_frame = False
                    ax.set_xlim(0, w * scale)
                    ax.set_ylim(0, h * scale)
                    ax.set_xlabel('X-axis (mm)')
                    ax.set_ylabel('Y-axis (mm)')
                    ax.set_title('Center of ARTag')
                    ax.grid(True)
                    plot = ax.scatter([], [], s = 10)
                center, rot = get_rotation_from_corners(corners[0])
                aruco.drawDetectedMarkers(frame, corners, ids)
                frame = cv2.circle(frame, (int(center[0]), int(center[1])), radius=5, color=(0, 0, 255), thickness=1)
                x_coords.append(center[0] * scale)
                y_coords.append(center[1] * scale)
                rotation.append(rot)
                plot.set_offsets(np.c_[x_coords, y_coords])
                plt.draw()
                plt.pause(0.001)

            cv2.imshow("image", frame)
            key = cv2.waitKey(1)
            if key == ord("q"):
                quit_early = True
                print("quit early, not saving data")
                break

        if not quit_early:
            if utils_file.isPath(f"{folder_name}/data.pickle"):
                saved_data = utils_file.openFile(folder_name)

                saved_data["noise_params"] = [w * scale, h * scale]
                saved_data["frames"] = frames
                saved_data["corners"] = cornerLst
                saved_data["ids"] = idsLst
                saved_data["x_coords"] = x_coords
                saved_data["y_coords"] = y_coords
                saved_data["rotation"] = rotation
        
                utils_file.saveFile(folder_name, saved_data)
            
            else:
                data = {"frames": frames, "corners": cornerLst, "ids": idsLst, "x_coords": x_coords, "y_coords": y_coords, "rotation": rotation, "noise_params": [w * scale, h * scale]}
                utils_file.saveFile(folder_name, data)
        
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Using Saved Data")
        fig, ax = plt.subplots()
        saved_data = utils_file.openFile(folder_name)
        frames = saved_data["frames"]
        cornerLst = saved_data["corners"]
        idsLst = saved_data["ids"]
        x_coords = saved_data["x_coords"]
        y_coords = saved_data["y_coords"]
        rotation = saved_data["rotation"]
        noise_params = saved_data["noise_params"]

        x_lim = noise_params[0]
        y_lim = noise_params[1]

        ax.set_xlim(0, x_lim)
        ax.set_ylim(0, y_lim)
        ax.set_xlabel('X-axis (mm)')
        ax.set_ylabel('Y-axis (mm)')
        ax.set_title('Center of ARTag')
        ax.grid(True)
        plot = ax.scatter(x_coords, y_coords, s = 10)
        plt.draw()
        plt.waitforbuttonpress(0)
        plt.close()