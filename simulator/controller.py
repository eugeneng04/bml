import robot_characterization
import numpy as np
from datetime import datetime

class pi_controller():
    def __init__(self, i, kp, ki):
        self.kp = kp #kp for p_controller
        self.ki = ki
        self.i = i #index of actuator
        self.funcs = robot_characterization.get_functions()
        self.exit = False
        self.prevOut = np.zeros(12)
        self.integral = 0
        self.prev_time = datetime.now()
    
    def set_target(self, target):
        self.integral = 0
        self.target = target    
        self.exit = False

    def compute(self, actualAngle): # we know that negative is ccw, positive is cw
        curr_time = datetime.now()
        delta_t = (curr_time - self.prev_time).total_seconds()
        error = self.target - actualAngle
        if abs(error) <= 1:
            self.exit = True
        p = self.kp * error
        self.integral = self.integral + self.ki * error * delta_t
        i = self.integral
        output = p + i
        self.prev_time = curr_time
        return output
    
   
    def convert(self, compute):
        print(compute)
        value = (compute) * 0.2
        if  self.target > 0: # odds negative, evens positive, cw postive, ccw negative
            self.prevOut[2 * self.i + 1] = value
            self.prevOut[2 * self.i] = 0
        else:
            self.prevOut[2 * self.i] = -value
            self.prevOut[2 * self.i + 1] =  0
        return self.prevOut



if __name__ == "__main__":
    controller = pi_controller(2, 1.5)
    controller.set_target(0)
    print(controller.convert(controller.compute(1)))
    # print(controller.convert(-1))
   
