import numpy as np


def log_delay(current, pF, p_decade):
    ''' y = a * x^-b '''
    a = pF / p_decade
    b = 1.1
    return a * current**(-b)


def log_delays(currents, pF, p_decade):
    ''' Currents needs to be a numpy array. '''
    currents = currents * 1e12
    delays = [int(log_delay(x, pF, p_decade) * 1e3) for x in currents]
    return delays


#print(log_delays(np.array([1, 1.6, 2.5, 4, 6.3, 10]) * 1e-12, 3.5, 5))
print(np.logspace(0, 1, num=6))
