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


# Testováno jen pro rozsahy 1eX až 1eY.
# TODO výhledově je potřeba nějak vyčíst sweep z keithleyho,
# spočítat mu delaye přesně a pak je zase nahrát zpátky.
# (Nebo zjistit přesně jak je staví s ohledem na "počet bodů na dekádu" při
# přesažení rozsahu.)
dr = delays_round(1e-11, 1e-10, 0, 15)
print("delays: ", dr)
print("len: ", len(dr))

decade_points = 5


#
# def kformat(number, precision):
#     form = '{:+.' + str(precision) + 'E}'
#     scientific = form.format(number)
#     keitheyific = scientific[0] + (11 - len(scientific)) * '0' + scientific[1:]
#     return keitheyific
#
#
# def shift_number_slow(s, order):
#     split = s.replace('E', '.').split('.')
#     precision = len(split[1])
#     number = float(s) * 10**order
#     return kformat(number, precision)
#

# def shift_number(s, order):
#     split = s.split('E')
#     original_order = int(split[-1])
#     new_order = original_order + order
#     split[-1] = "{:+03d}".format(new_order)
#     return 'E'.join(split)
#
#
# def shift_data(raw_data, cols=5, shift=-3):
#     '''Přenásobí hodnoty proudu o >shift< řádů (kompenzace děliče).'''
#     a = raw_data.split(',')
#     x_frequencies = {5: 2, 7: 3, 13: 3, 15: 4}
#     freq = x_frequencies[cols]
#     a[::freq] = [shift_number(c, shift) for c in a[::freq]]
#     return ','.join(a)
#
#
# inp = "+10.000E-06,+005.008E+00,+09.900E-06,+005.036E+00,+09.800E-06,+005.132E+00"
# print(inp)
# print(shift_data(inp, cols=5, shift=-3))

# +005.036E+00
