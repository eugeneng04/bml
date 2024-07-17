import numpy as np

#takes raw bytes from naneye camera and turns it into a frame for cv2
def convertToImage(data):
    array = np.frombuffer(data, dtype=np.uint8)

    b = np.reshape(array[0::4], (int(len(array) ** 0.5) // 2, int(len(array) ** 0.5) // 2))
    g = np.reshape(array[1::4], (int(len(array) ** 0.5) // 2, int(len(array) ** 0.5) // 2))
    r = np.reshape(array[2::4], (int(len(array) ** 0.5) // 2, int(len(array) ** 0.5) // 2))

    frame = np.dstack((r, g, b))
    return frame

def upscaleImage(img, scale):
    return img.repeat(scale, axis=0).repeat(scale, axis=1)

