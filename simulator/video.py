import cv2
import cv2.aruco as aruco
import numpy as np
import matplotlib.pyplot as plt

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

cap = cv2.VideoCapture(0)

first_frame = True

fig, ax = plt.subplots()

#arbitrary id mappings: 0 -> zero point, 1 -> first joint, 2->second joint, 3-> third joint, 4-> fourth joint

while True:
    ret, frame = cap.read()
    if not ret:
        break

    corners, ids, c = detect_aruco_tag(frame)
    if ids is not None:
        if first_frame and (0 in ids):
            zero_index = ids.index(0)
            h, w, *_ = frame.shape
            scale = pixelToMM(corners[zero_index], 3) # change size of artag here
            first_frame = False
            ax.set_xlim(0, w * scale)
            ax.set_ylim(0, h * scale)
            ax.set_xlabel('X-axis (mm)')
            ax.set_ylabel('Y-axis (mm)')
            ax.set_title('Center of ARTag')
            ax.grid(True)
            plot = ax.scatter([], [], s = 10)
        
        for i in range(len(ids)):
            if ids[i] is not 0:
                center, rot = get_rotation_from_corners(corners[i])
                aruco.drawDetectedMarkers(frame, corners[i], ids[i])
                plt.scatter(center, label = f"id: {ids[i]}")

        plt.draw()
        plt.delay(0.01)

        cv2.imshow("image", frame)
        key = cv2.waitKey(1)
        if key == ord("q"):
            quit_early = True
            print("quit early, not saving data")
            break

        
