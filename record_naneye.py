import cv2
import cv2.aruco as aruco
import numpy as np
from utils_data_process import cmp_corners
import matlabInst
import socketComm
import utils_naneye
import argparse
import time
import pickle
import utils_output

def detect_aruco_tag(frame):
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters =  aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary, parameters)
    return detector.detectMarkers(frame)

def displayArucoTag(corners, ids):  
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

    parser = argparse.ArgumentParser()
    
    parser.add_argument("comment", help = "comment to add to filename")
    parser.add_argument("live", help = "True/False values for live ARTag streaming")

    frame_size = (250, 250) #hardcoded for naneye

    logs_dir = utils_output.createLogFolder()

    folder_name = f"{logs_dir}_{parser.parse_args().comment}"
    try:
        output = cv2.VideoWriter(
            f'{folder_name}/video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 60, frame_size)
    except Exception as e:
        print(f"Error creating VideoWriter: {e}")

    #initialize and run matlab file
    mat = matlabInst.matlabInst()
    mat.runMatlabCommand("streamNaneyeImage(false)")
    #wait for matlab file to initialize
    time.sleep(15)

    #create and connect socket object
    sock = socketComm.socketComm("127.0.0.1", 8888)
    sock.connect()

    frames = []
    if parser.parse_args.live:
        cornersLst = []
        idsLst = []
    

    while True:
        try:
            #read 250000 bytes: full image from naneye camera
            data = sock.readnbytes(250000)

            #convert from bytes to image
            
            frame = utils_naneye.convertToImage(data)

            #add bounding box to ARTag

            output.write(frame)
            frames.append(frame)

            if parser.parse_args().live:
                corners, ids, c = detect_aruco_tag(frame)
                displayArucoTag(corners, ids)
                cornersLst.append(corners)
                idsLst.append(ids)

            frame = utils_naneye.upscaleImage(frame, 2)
            cv2.imshow("image", frame)

            key = cv2.waitKey(1)
            if key == ord("q"):
                #sock.close()
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    if parser.parse_args.live:
        data = {"frames": frames, "corners": cornersLst, "ids": idsLst}
    else:
        data = {"frames": frames}
    try:
        with open(f'{folder_name}/data.pickle', 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(f"error with saving data: {e}")
    output.release()
    cv2.destroyAllWindows()