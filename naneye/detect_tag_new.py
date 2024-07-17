import cv2
import cv2.aruco as aruco
import numpy as np
from utils_data_process import cmp_corners
import matlabInst
import socketComm
import utils_naneye
import time

def detect_aruco_tag(frame):
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters =  aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary, parameters)
    return detector.detectMarkers(frame)

def displayArucoTag(frame):  
    corners, ids, c = detect_aruco_tag(frame)
    aruco.drawDetectedMarkers(frame, corners, ids)

    if len(corners) > 0:
        corners = np.array(corners)[:, 0, :]
        ids = np.array(ids)[:, 0]
        corners_by_id = {}
        for j, tmp_id in enumerate(ids):
            corners_by_id[tmp_id] = corners[j]
        if 1 in corners_by_id and 3 in corners_by_id:
            print(cmp_corners(corners_by_id[1], corners_by_id[3])['rot'])

if __name__ == "__main__":
    #initialize and run matlab file
    mat = matlabInst.matlabInst()
    mat.runMatlabCommand("streamNaneyeImage(false)")
    #wait for matlab file to initialize
    time.sleep(15)

    #create and connect socket object
    sock = socketComm.socketComm("127.0.0.1", 8888)
    sock.connect()

    while True:
        try:
            #read 250000 bytes: full image from naneye camera
            data = sock.readnbytes(250000)

            #convert from bytes to image
            frame = utils_naneye.convertToImage(data)

            #add bounding box to ARTag
            displayArucoTag(frame)

            frame = utils_naneye.upscaleImage(frame, 2)
            cv2.imshow("image", frame)

            key = cv2.waitKey(1)
            if key == ord("q"):
                sock.close()
                break
        except Exception as e:
            print(f"Error: {e}")
            break
    
    cv2.destroyAllWindows()


