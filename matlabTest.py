import subprocess

matlab_executable = 'matlab.exe'

matlab_script = 'naneyetest2'

command = [matlab_executable, '-nosplash', '-nodesktop', '-r', f'{matlab_script}']

process = subprocess.Popen(command)

process.wait()

