import matlab.engine
import time
import socket
import numpy as np
import cv2
import threading

#eng = matlab.engine.start_matlab()

#eng.naneyetest(nargout = 0)
#
#matlab_thread = threading.Thread(eng.naneyeTest(nargout = 0))
#matlab_thread.start()
#eng.naneyeTest(nargout = 0)

#naneye = eng.naneyeConstruct(nargout = 1)
# print(naneye)
# while True:
#     output = eng.outputdata(naneye, nargout = 1)
#     print(output)
#     time.sleep(1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(('127.0.0.1', 8888))
    print("Connection to server established!")
    data = sock.recv(80000)
    #print('Received', repr(data))
    byte_data = bytes.fromhex(str(data.hex()))

    # Convert bytes to numpy array of integers
    array = np.frombuffer(byte_data, dtype=np.uint8)

    # Reshape the
    #  1D array into a 250x250 array
    #array = array.reshape((256, 256))
    # Reshape the byte array to separate the channels
    b = np.reshape(array[0::4], (128, 128)).T
    g = np.reshape(array[1::4], (128, 128)).T
    r = np.reshape(array[2::4], (128, 128)).T

    # Combine the channels into an RGB image  
    imgh = np.dstack((r, g, b))

    # Now you have the 250x250 array where the values range from 0 to 255

    #print(imgh)

    cv2.imshow('Image', imgh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
        
