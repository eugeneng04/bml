import os
from datetime import datetime

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