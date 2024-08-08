import matplotlib.pyplot as plt
import numpy as np
import cv2
import cv2.aruco as aruco
from math import atan2, degrees
import time

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

def getAngle(center1, center2, center3):
    # a = [center2[0] - center1[0], center2[1] - center1[1]]
    # b = [center2[0] - center3[0], center2[1] - center3[1]]
    # a_dot_b = np.dot(a, b)
    # one_norm_a = np.linalg.norm(a, 1)
    # one_norm_b = np.linalg.norm(b, 1)
    # angle = np.arccos((a_dot_b) / (one_norm_a * one_norm_b))
    # return np.rad2deg(angle)

    x1, y1 = center1
    x2, y2 = center2
    x3, y3 = center3
    deg1 = (360 + degrees(atan2(x1 - x2, y1 - y2))) % 360
    deg2 = (360 + degrees(atan2(x3 - x2, y3 - y2))) % 360
    return 180 - (deg2 - deg1) if deg1 <= deg2 else 180 -(360 - (deg1 - deg2))

tag_dict = {4: 0, # key: actual tag, value = index of robot
            2: 1,
            3: 2,
            17: 3,
            10: 4,
            5: 5}


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def calcAngle(): #Thread
    #frame = cv2.imread("test_data_1.jpg")
    while True:
        ret, frame = cap.read()
        corners, ids, c = detect_aruco_tag(frame)
        if ids is not None:
            aruco.drawDetectedMarkers(frame, corners, ids)
            centerDict = {}
            for i in range(len(ids)):
                center, rot = get_rotation_from_corners(corners[i])
                if int(ids[i][0]) in tag_dict:
                    centerDict[tag_dict[int(ids[i][0])]] = center

            cv2.imshow("img", frame)
            key = cv2.waitKey(1)
            if key == ord("q"):
                quit_early = True
                break
            angleArr = []
            for i in range(len(centerDict) - 2):
                angleArr.append(getAngle(centerDict[i], centerDict[i+1], centerDict[i+2]))

            print(angleArr)

def calcAngleLive():
    ret, frame = cap.read()
    corners, ids, c = detect_aruco_tag(frame)
    if ids is not None:
        aruco.drawDetectedMarkers(frame, corners, ids)
        centerDict = {}
        for i in range(len(ids)):
            center, rot = get_rotation_from_corners(corners[i])
            if int(ids[i][0]) in tag_dict:
                centerDict[tag_dict[int(ids[i][0])]] = center

        angleArr = []
        for i in range(len(centerDict) - 2):
            angleArr.append(getAngle(centerDict[i], centerDict[i+1], centerDict[i+2]))

        return(angleArr)

def calcAngleSingle(frame):
    corners, ids, c = detect_aruco_tag(frame)
    if ids is not None:
        aruco.drawDetectedMarkers(frame, corners, ids)
        centerDict = {}
        for i in range(len(ids)):
            center, rot = get_rotation_from_corners(corners[i])
            if int(ids[i][0]) in tag_dict:
                centerDict[tag_dict[int(ids[i][0])]] = center

        #cv2.imshow("img", frame)
        # key = cv2.waitKey(0)
        # if key == ord("q"):
        #     quit_early = True
        angleArr = []
        for i in range(len(centerDict) - 2):
            angleArr.append(getAngle(centerDict[i], centerDict[i+1], centerDict[i+2]))

        return(angleArr)

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    #frame = cv2.imread("test_data_1.jpg")
    while True:
        ret, frame = cap.read()
        corners, ids, c = detect_aruco_tag(frame)
        print(corners, ids)
        aruco.drawDetectedMarkers(frame, corners, ids)
        pltobjects = []
        centerDict = {}
        for i in range(len(ids)):
            center, rot = get_rotation_from_corners(corners[i])
            #print(center)
            if int(ids[i][0]) in tag_dict:
                centerDict[tag_dict[int(ids[i][0])]] = center
            #     pltobjects.append(plt.scatter(center[0], center[1], label = f"id: {ids[i]}", color = "red"))
            # plt.legend()       
            # plt.draw()

        # print(centerDict)
        cv2.imshow("img", frame)
        # plt.show()
        key = cv2.waitKey(1)
        if key == ord("q"):
            quit_early = True
            break
        angleArr = []
        for i in range(len(centerDict) - 2):
            #print(centerDict[i], centerDict[i+1], centerDict[i+2])
            angleArr.append(getAngle(centerDict[i], centerDict[i+1], centerDict[i+2]))

        print(angleArr)
        time.sleep(1)

