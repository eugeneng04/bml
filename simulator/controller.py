import robot_characterization
import numpy as np
from datetime import datetime

class pid_controller():
    def __init__(self, i, kp, ki, kd):
        self.kp = kp #kp for p_controller
        self.ki = ki
        self.kd = kd

        self.i = i #index of actuator

        self.funcs = robot_characterization.get_functions()

        self.exit = False

        self.prevOut = np.zeros(12)
        self.prevOut[11] = 10

        self.integral = 0
        self.prev_time = datetime.now()
        self.error = 0
    
    def set_target(self, target):
        self.integral = 0
        self.target = target    
        self.exit = False

    def compute(self, actualAngle): # we know that negative is ccw, positive is cw
        curr_time = datetime.now()
        delta_t = (curr_time - self.prev_time).total_seconds()
        prev_error = self.error

        error = self.target - actualAngle
        self.error = error
        if abs(error) <= 1:
            self.exit = True
        p = self.kp * error
        self.integral = self.integral + self.ki * error * delta_t
        i = self.integral
        d = (self.kd * (error - prev_error))/delta_t
        output = p + i + d
        self.prev_time = curr_time
        return output
    
   
    def convert(self, value):
        if self.target > 0: # odds negative, evens positive, cw postive, ccw negative.
            # problem here is resetting angle when target is still positive and error is negative
            if self.error > 0:
                self.prevOut[2 * self.i + 1] = value
            else:
                self.prevOut[2 * self.i + 1] = -value
            self.prevOut[2 * self.i] = 0
        else:
            if self.error < 0:
                self.prevOut[2 * self.i] = -value
            else:
                self.prevOut[2 * self.i] = value
            self.prevOut[2 * self.i + 1] =  0
        return self.prevOut



if __name__ == "__main__":
    controller = pid_controller(2, 1.5)
    controller.set_target(0)
    print(controller.convert(controller.compute(1)))
    # print(controller.convert(-1))
   
