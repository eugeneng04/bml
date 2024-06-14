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
    #while True:
    data = readnbyte(sock, 250000)
    #print('Received', repr(data)))

    # Convert bytes to numpy array of integers
    array = np.frombuffer(data, dtype=np.uint8)
    filename = './output_python.txt'
    np.savetxt(filename, array , fmt='%d', delimiter='\t')

    # Write the data to the text file
    # print(array)
    # print(len(array))
    # print(array.shape)
    # Reshape the
    #  1D array into a 250x250 array
    #array = array.reshape((256, 256))
    # Reshape the byte array to separate the channels
    b = np.reshape(array[0::4], (int(len(array) ** 0.5) // 2, int(len(array) ** 0.5) // 2))
    g = np.reshape(array[1::4], (int(len(array) ** 0.5) // 2, int(len(array) ** 0.5) // 2))
    r = np.reshape(array[2::4], (int(len(array) ** 0.5) // 2, int(len(array) ** 0.5) // 2))

    # Specify the file name

    # np.savetxt("out_python_b.txt", b , fmt='%d', delimiter='\t')
    # np.savetxt("out_python_g.txt", g , fmt='%d', delimiter='\t')
    # np.savetxt("out_python_r.txt", r , fmt='%d', delimiter='\t')
    # Export the flattened image to a text file
    imgh = cv2.merge((r, g, b))
    imgh_dstack = np.dstack([r,g,b])
    print(imgh == imgh_dstack)
    # Now you have the 250x250 array where the values range from 0 to 255

    #print(imgh)

    cv2.namedWindow('Image', imgh)
    cv2.resizeWindow('image', 500,500)
    cv2.waitKey(0)
        
        


