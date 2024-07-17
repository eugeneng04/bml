import socket
import time
import numpy as np

class socketComm():
    #intialize socket object
    def __init__(self, ip = "127.0.0.1", port = 8888):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    #connect to TCP server
    def connect(self):
        self.socket.connect((self.ip, self.port))
        print("Successfully Connected")

    #read specifically n bytes (for camera), outputs bytes
    def readnbytes(self, n):
        buff = bytearray(n)
        pos = 0
        while pos < n:
            cr = self.socket.recv_into(memoryview(buff)[pos:])
            if cr == 0:
                raise EOFError
            pos += cr
        return buff
    def close(self):
        self.socket.close()
