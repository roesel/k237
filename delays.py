# -*- coding: utf-8 -*-
import numpy as np
from io import StringIO   # StringIO behaves like a file object
import numpy as np
import math


def log_delay(current, pF, p_decade):
    ''' y = a * x^-b '''
    a = pF / p_decade
    b = 1.1
    return a * current**(-b)


def log_delays(currents, pF, p_decade):
    ''' Currents needs to be a numpy array. '''
    currents = currents * 1e12
    delays = np.array([int(log_delay(x, pF, p_decade) * 1e3) for x in currents])
    return delays


def calc_delays(sw_min, sw_max, decade, pF):
    ''' Simple delay calculation with a factor of 3 to fit excel predictions. '''

    points = {0: 5, 1: 10, 2: 25, 3: 50}
    decade_points = points[decade]
    mind = math.floor(np.log10(sw_min))
    maxd = math.ceil(np.log10(sw_max))
    num_of_decades = abs(mind - maxd)
    longer_currents = np.logspace(mind, maxd, num=num_of_decades * decade_points + 1)
    # get rid of all values out of range
    fake_currents = longer_currents[np.where(longer_currents <= sw_max)]
    delays = log_delays(fake_currents, pF, decade_points)
    delays = 3 * delays
    # replace all "0 ms" with "1 ms"
    delays[delays == 0] = 1
    return delays


def calc_reverse(array):
    array = np.rint((2 / 3 * array)).astype(int, copy=False)
    return array


def mod_bias(original_delays):
    ''' Multiplies the first delay by 4 in order to create BIAS level before measurement. '''
    delays = np.copy(original_delays)
    delays[0] = delays[0] * 4
    return delays


def delays_round(sw_min, sw_max, decade, pF):
    ''' Returns delays for round trip from sw_min to sw_max and back for log
    measurement at capacity pF.'''
    arr = calc_delays(sw_min, sw_max, decade, pF)
    there = mod_bias(arr)
    back = calc_reverse(arr)
    return np.concatenate([there, back[::-1]], axis=0)


def delays_up(sw_min, sw_max, decade, pF):
    ''' Returns delays for trip up from sw_min to sw_max for log
    measurement at capacity pF.'''
    arr = calc_delays(sw_min, sw_max, decade, pF)
    there = mod_bias(arr)
    return there


def delays_down(sw_min, sw_max, decade, pF):
    ''' Returns delays for trip down from sw_max to sw_min and back for log
    measurement at capacity pF.'''
    arr = calc_delays(sw_min, sw_max, decade, pF)
    back = calc_reverse(arr)
    biased = mod_bias(back)
    return biased
