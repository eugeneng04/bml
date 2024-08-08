import robot_characterization
import numpy as np

class p_controller():
    def __init__(self, i, kp):
        self.kp = kp #kp for p_controller
        self.i = i #index of actuator
        self.funcs = robot_characterization.get_functions()
        self.exit = False
    
    def set_target(self, target):
        self.target = target    
        self.exit = False

    def compute(self, actualAngle): # we know that negative is ccw, positive is cw
        error = self.target - actualAngle
        if abs(error) <= 1:
            self.exit = True
        output = self.kp * error
<<<<<<< HEAD
        return actualAngle + output
=======
        print(output)
        return actualAngle -output
>>>>>>> 927b96f741a3694771d39fb2634c6339e246e6c1
    
    def convert(self, compute): # return pressure values
        out = np.zeros(12)
        if compute > 0:
            out[2*self.i + 1] = self.funcs[2 * self.i + 1]((compute)) # angle to pressure conversion function
        else:
            out[2*self.i] = self.funcs[2 * self.i](-(compute))

        return out


if __name__ == "__main__":
    controller = p_controller(2, 1.5)
    controller.set_target(0)
    print(controller.convert(controller.compute(1)))
    # print(controller.convert(-1))
   
