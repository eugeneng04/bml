import utils_file
import cv2
import characterization
import numpy as np

folder_name = f"{utils_file.getCurrPath()}/logs/test"

print("Using Saved Data")
saved_data = utils_file.openFile(f"{folder_name}")

outputArr = [([], []) for i in range(8)]

for val in range(len(saved_data["dumpOut"])):
    filename = folder_name + saved_data["dumpOut"][val][1]
    frame = cv2.imread(filename)
    try:
        angles = characterization.calcAngleSingle(frame)

        for i in range(len(saved_data["dumpOut"][val][0])):
            if saved_data["dumpOut"][val][0][i] != 0.0: # calculates which actuator is non-zero, only works if all are zero except for 1
                outputArr[i][0].append(saved_data["dumpOut"][val][0][i])
                outputArr[i][1].append(abs(angles[i//2]))
    except:
        pass


saved_data["characterization"] = outputArr
utils_file.saveFile(folder_name, saved_data)
print(outputArr)


