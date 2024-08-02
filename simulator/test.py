import utils_file
import cv2

folder_name = f"{utils_file.getCurrPath()}/logs/test"

video = cv2.VideoCapture(1, cv2.CAP_DSHOW)
ret, frame = video.read()
if not ret:
    print("failed to grab frame")

img_name = f"{folder_name}/images/capture.png"
