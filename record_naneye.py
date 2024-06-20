# plan is to have files that can record naneye data -> get raw data
# files that do data processing on the raw data
# save data to buffer -> pickle dump so we don't have to do aruco processing multiple times

import cv2
import cv2.aruco as aruco
import numpy as np
from utils_data_process import cmp_corners
import matlabInst
import socketComm
import utils_naneye
import time
import argparse
import datetime


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    
    parser.add_argument("comment", help = "comment to add to filename")

    frame_size = (250, 250) #hardcoded for naneye
    output = cv2.VideoWriter(f'./logs/{datetime.now().strftime("%Y-%m-%d_%H%M%S")}_{parser.parse_args().comment}', cv2.VideoWriter_fourcc('M','J','P','G'), 60, frame_size)

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
            #displayArucoTag(frame)
            output.write(frame)
            frame = utils_naneye.upscaleImage(frame, 2)
            cv2.imshow("image", frame)

            key = cv2.waitKey(1)
            if key == ord("q"):
                sock.close()
                break
        except Exception as e:
            print(f"Error: {e}")
            break
    output.release()
    cv2.destroyAllWindows()