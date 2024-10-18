import cv2
import cv2.aruco as aruco
import numpy as np
import matplotlib.pyplot as plt
import utils_data_process
import threading

def detect_aruco_tag(frame):
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    # dictionary = aruco.extendDictionary(30, 3)

    # dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
    parameters =  aruco.DetectorParameters()
    # parameters.polygonalApproxAccuracyRate=0.05
    detector = aruco.ArucoDetector(dictionary, parameters)
    return detector.detectMarkers(frame)

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

def video_thread():
    camera_id = 1
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("image", frame)
        key = cv2.waitKey(1)
        if key == ord("q"):
            quit_early = True
            break


def temp():

    camera_id = 0
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)

    first_frame = True

    fig, ax = plt.subplots()

    base_tag = 2
    slider_tag = 17
    moving_tag = 10
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("image", frame)
        key = cv2.waitKey(1)
        if key == ord("q"):
            quit_early = True
            break

        corners, ids, c = detect_aruco_tag(frame)
        #print(corners, ids)
        if ids is not None: 
            if first_frame and (2 in ids): # get the scale
                base_index = np.where(ids == base_tag)[0][0]
                h, w, *_ = frame.shape
                scale = pixelToMM(corners[base_index], 4.5) # change size of artag here
                print(f"scale: {scale}")
                first_frame = False
                ax.set_xlim(0, w * scale)
                ax.set_ylim(0, h * scale)
                ax.set_xlabel('X-axis (mm)')
                ax.set_ylabel('Y-axis (mm)')
                ax.set_title('Center of ARTag')
                ax.grid(True)

        if ids is not None:
            if moving_tag in ids and slider_tag in ids:
                moving_index = np.where(ids == moving_tag)[0][0]
                slider_index = np.where(ids == slider_tag)[0][0]

                moving_coords = corners[moving_index]
                slider_coords = corners[slider_index]
                distance = ((moving_coords - slider_coords) * scale)[0][0][0]
                print(distance)

            aruco.drawDetectedMarkers(frame, corners, ids)
            pltobjects = []

            for i in range(len(ids)):
                center, rot = get_rotation_from_corners(corners[i])
                pltobjects.append(plt.scatter(center[0] * scale, center[1] * scale, label = f"id: {ids[i]}", color = "red"))
            plt.legend()       
            plt.draw()
            plt.pause(0.01)
            for i in pltobjects:
                i.remove()

        cv2.imshow("image", frame)
        key = cv2.waitKey(1)
        if key == ord("q"):
            quit_early = True
            break

            
if __name__ == "__main__":
    temp()