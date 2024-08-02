import scipy.interpolate
import matplotlib.pyplot as plt
import numpy as np

def interp(x_vals, y_vals):
    return scipy.interpolate.interp1d(x_vals, y_vals, fill_value = "extrapolate", kind = "cubic")

def display():
    x_vals = [0, 5, 10, 15, 20, 25, 30]

    f, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8)) = plt.subplots(4, 2, sharey=True)

    x_interp = np.linspace(np.min(x_vals), np.max(x_vals), 100)
    act_1 = [0, 20, 38, 50, 63, 67, 70]

    act_1_f = interp(x_vals, act_1)
    act_1_interp = act_1_f(x_interp)
    ax1.plot(x_vals, act_1, 'o', x_interp, act_1_interp, '-')

    act_2 = [0, 5, 14, 23, 27, 30, 33]

    act_2_f = interp(x_vals, act_2)

    act_2_interp = act_2_f(x_interp)
    ax2.plot(x_vals, act_2, 'o', x_interp, act_2_interp, '-')

    act_3 = [0, 10, 28, 43, 60, 66, 70]

    act_3_f = interp(x_vals, act_3)

    act_3_interp = act_3_f(x_interp)
    ax3.plot(x_vals, act_3, 'o', x_interp, act_3_interp, '-')

    act_4 = [0, 11, 24, 35, 49, 50]


    act_4_f = interp(x_vals[:-1], act_4)

    act_4_interp = act_4_f(x_interp)
    ax4.plot(x_vals[:-1], act_4, 'o', x_interp, act_4_interp, '-')

    act_5 = [0, 4, 17, 32, 40, 43, 45]


    act_5_f = interp(x_vals, act_5)

    act_5_interp = act_5_f(x_interp)
    ax5.plot(x_vals, act_5, 'o', x_interp, act_5_interp, '-')

    act_6 = [0, 0, 5, 22, 42, 43, 48]

    act_6_f = interp(x_vals, act_6)

    act_6_interp = act_6_f(x_interp)
    ax6.plot(x_vals, act_6, 'o', x_interp, act_6_interp, '-')

    act_7 = [0, 1, 9, 19, 25, 32, 35]

    act_7_f = interp(x_vals, act_7)

    act_7_interp = act_7_f(x_interp)
    ax7.plot(x_vals, act_7, 'o', x_interp, act_7_interp, '-')

    act_8 = [0, 1, 17, 30, 40, 43, 49]

    act_8_f = interp(x_vals, act_8)

    act_8_interp = act_8_f(x_interp)
    ax8.plot(x_vals, act_8, 'o', x_interp, act_8_interp, '-')

    plt.show()

def get_functions():
    x_vals = [0, 5, 10, 15, 20, 25, 30]
    act_1 = [0, 28 ,44, 59, 68 ,70, 71]
    act_2 = [0, 8, 16, 25, 29, 33, 35]
    act_3 = [0, 20, 39, 52, 70, 72, 76]
    act_4 = [0, 12 ,31 ,47, 60 ,61 , 55] # edited
    act_5 = [0, 8 ,26, 40, 47, 48, 50]
    act_6 = [0, 1, 18, 26 ,46 ,47, 52]
    act_7 = [0, 5 ,15, 25 ,29, 37,38]
    act_8 = [0, 13 ,23, 36, 44, 45, 50]
    lst = [act_1, act_2, act_3, act_4, act_5, act_6, act_7, act_8]

    return [interp(act, x_vals) for act in lst]


