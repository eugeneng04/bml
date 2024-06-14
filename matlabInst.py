import subprocess

#runs matlab comand
class matlabInst():
    def __init__(self, matlab_executable = "matlab.exe"):

        self.matlab_executable = matlab_executable

    #takes matlab command and runs it 
    def runMatlabCommand(self, command):
        #runs matlab command in the MATLAB folder
        command = [self.matlab_executable, '-nosplash', '-nodesktop', '-r', f'cd MATLAB; {command};, exit;']

        self.process = subprocess.Popen(command)

        return self.process
    
    #kills current matlab instance
    def killMatlab(self):
        self.process.kill()
        outs, errs = self.process.communicate()