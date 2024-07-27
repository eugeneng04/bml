import serial, time

ser = serial.Serial("/dev/cu.usbmodem1101", baudrate = 115200)
time.sleep(2)

global running

def setMaxSpeed(speed):
    ser.write(f's mrpm {speed}'.encode())

def setMaxVelocity(v):
    ser.write(f's mv {v}'.encode())

def setStepsPerRev(spr):
    ser.write(f's spr {spr}'.encode())

def setSpeed(speed):
    ser.write(f's sr {speed}'.encode())

def setVelocity(v):
    ser.write(f's sv {v}'.encode())

def moveDistance(d):
    global running
    ser.write(f'm d {d}'.encode())
    running = True
    while True:
        byte = ser.readline()
        #byte = ser.read()
        print(byte.decode('utf-8'))
        if byte.decode() == "done\r\n":
        #if byte.decode() == "1":
            running = False
            ser.flush()
            break

def moveRotations(r):
    ser.write(f'm r {r}'.encode())

def isRunning():
    global running
    return running

def readThread():
    global running
    if ser.in_waiting:
        byte = ser.read()
        if byte == 1:
            running = False

