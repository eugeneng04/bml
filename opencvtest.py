import matlab.engine
import os

eng = matlab.engine.start_matlab()

#eng.naneyetest(nargout = 0)

# naneye = eng.naneyeConstruct(nargout = 1)
# print(naneye)
# output = eng.outputdata(naneye)
# print(output)
eng.naneyeTest(nargout = 0)