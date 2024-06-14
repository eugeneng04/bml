import cv2
import cv2.aruco as aruco
import numpy as np
from utils_data_process import cmp_corners
import socket
import time
import subprocess

matlab_executable = 'matlab.exe'

matlab_script = 'streamNaneyeImage(false)'

command = [matlab_executable, '-nosplash', '-nodesktop', '-r', f'cd MATLAB; {matlab_script};, exit;']

process = subprocess.Popen(command)

time.sleep(15)


def detect_aruco_tag(frame):
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters =  aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary, parameters)
    return detector.detectMarkers(frame)

init_corners=None
def readnbyte(sock, n):
    buff = bytearray(n)
    pos = 0
    while pos < n:
        cr = sock.recv_into(memoryview(buff)[pos:])
        if cr == 0:
            raise EOFError
        pos += cr
    return buff

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(('127.0.0.1', 8888))
    print("Connection to server established!")
    frame_count = 0
    start_time = time.time()
    fps = 0
    while(True):
        try:
            # Capture an image from the camera
            data = readnbyte(sock, 250000)
            #data = sock.recv(250000)
            frame_count += 1
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1.0:
                fps = frame_count / elapsed_time
                
                frame_count = 0
                start_time = time.time()
            print(f"FPS: {fps}")
            #array = np.frombuffer(data, dtype=np.uint8)
            array = data
            
            b = np.reshape(array[0::4], (int(len(array) ** 0.5) // 2, int(len(array) ** 0.5) // 2))
            g = np.reshape(array[1::4], (int(len(array) ** 0.5) // 2, int(len(array) ** 0.5) // 2))
            r = np.reshape(array[2::4], (int(len(array) ** 0.5) // 2, int(len(array) ** 0.5) // 2))

            imgh = np.dstack((r, g, b))
            frame = imgh

            # print(frame.dtype, frame.shape)
            # Check if the image is captured successfully
                
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
            cv2.imshow('image', imgh)
            
            # Wait for a key press
            key = cv2.waitKey(1)

            # Exit the loop if the "q" key is pressed
            if key == ord("q"):
                sock.close()
                break
        except Exception as e:
            print(e)
            break


# Release the VideoCapture object and close all windows
cv2.destroyAllWindows()