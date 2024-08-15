import cv2
import cv2.aruco as aruco
import numpy as np
import matplotlib.pyplot as plt
import utils_data_process

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


camera_id = 0
cap = cv2.VideoCapture(camera_id)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)




first_frame = True

fig, ax = plt.subplots()

#arbitrary id mappings: 0 -> zero point, 1 -> first joint, 2->second joint, 3-> third joint, 4-> fourth joint
id_lst = [3, 17, 10, 5]
while True:
    ret, frame = cap.read()
    if not ret:
        break

    corners, ids, c = detect_aruco_tag(frame)
    if ids is not None:
        id_to_corner = {}

        for i in range(len(ids)):
            id_to_corner[int(ids[i][0])] = corners[i][0]
        
        angles = []
        angles_relative = []
        
        for i in range(len(id_lst)):
            if 4 in id_to_corner and id_lst[i] in id_to_corner:
                angle = utils_data_process.cmp_corners(id_to_corner[4], id_to_corner[id_lst[i]])["rot"]
                angles.append(angle)
                if i == 0:
                    angles_relative.append(angle)
                else:
                    angles_relative.append(angles[i] - angles[i - 1])
        
        print(angles_relative)
            
    aruco.drawDetectedMarkers(frame, corners, ids)

    cv2.imshow("image", frame)
    key = cv2.waitKey(1)
    if key == ord("q"):
        quit_early = True
        break

        
