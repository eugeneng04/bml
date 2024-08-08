import os
from datetime import datetime
import pickle
import argparse

def createLogFolder(name = datetime.now().strftime("%Y-%m-%d_%H%M%S")):
    logs_dir = os.path.join(os.getcwd(), f'logs/{name}')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

def isPath(name):
    return os.path.exists(name)

def getCurrPath():
    return os.getcwd()

def fileExists(name):
    return os.path.isfile(name)

# def genArgparse():
#     parser = argparse.ArgumentParser()
    
#     parser.add_argument("comment", help = "comment to add to filename")
#     parser.add_argument("live", help = "True/False values for live ARTag streaming")
    
#     return parser

def validData(folder_name, arg):
    if fileExists(f"{folder_name}/data.pickle"):
        with open(f'{folder_name}/data.pickle', 'rb') as data:
            saved_data = pickle.load(data)
            if saved_data.get(arg) is not None:
                return True
    return False

def openFile(folder_name):
    return pickle.load(open(f'{folder_name}/data.pickle', 'rb'))

def saveFile(folder_name, data):
    with open(f'{folder_name}/data.pickle', 'wb') as handle:
                    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def pathLogic(path):
    print(path)
    isExist = os.path.exists(path)
    if not isExist:
        print(f"created directory: {path}!")
        os.makedirs(path)