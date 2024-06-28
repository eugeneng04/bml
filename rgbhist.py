import cv2
import numpy as np
import matplotlib.pyplot as plt
import argparse
import utils_file

def genHistogram(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    color = ("blue", "green", "red")
    out = []
    for i, col in enumerate(color):
        hist_ = cv2.calcHist([frame], [i], None, [256], [2,256])
        out.append(hist_)

def displayHist(hist):
    color = ("blue", "green", "red")
    for i, col in enumerate(color):
                plt.plot(hist[i], color = col)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("name", help = "folder for name of file")
    parser.add_argument("--dump", action="store_false", help = "whether to use saved output")
    folder_name = f"{utils_file.getCurrPath()}/logs/{parser.parse_args().name}"
    
    flag = utils_file.validData(folder_name, "hists")

    if (parser.parse_args().dump or not flag):
        frames = []
        hists = []
        cap = cv2.VideoCapture(f"{folder_name}/video.avi")
        fig, ax = plt.subplots()
        plt.xlim([0,256])
        plt.title("RGB Values")

        while True:
            ret, frame = cap.read()
            frames.append(frame)
            if not ret:
                break
            
            hist = genHistogram(frame)
            hists.append(hist)
            displayHist(hist)

        if utils_file.isPath(f"{folder_name}/data.pickle"):
                saved_data = utils_file.openFile(folder_name)

                saved_data["frames"] = frames
                saved_data["hists"] = hists
        
                utils_file.saveFile(folder_name, saved_data)
            
        else:
            data = {"frames": frames, "hists": hists}
            utils_file.saveFile(folder_name, data)
    
    else:
        print("Using Saved Data")
        fig, ax = plt.subplots()
        saved_data = utils_file.openFile(folder_name)
        hists = saved_data["hists"]
        for hist in hists:
             displayHist(hist)


