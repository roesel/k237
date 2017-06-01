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
#print(np.logspace(0, 1, num=6))


def kformat(number, precision):
    form = '{:+.' + str(precision) + 'E}'
    scientific = form.format(number)
    keitheyific = scientific[0] + (11 - len(scientific)) * '0' + scientific[1:]
    return keitheyific


def shift_number_slow(s, order):
    split = s.replace('E', '.').split('.')
    precision = len(split[1])
    number = float(s) * 10**order
    return kformat(number, precision)


def shift_number(s, order):
    split = s.split('E')
    original_order = int(split[-1])
    new_order = original_order + order
    split[-1] = "{:+03d}".format(new_order)
    return 'E'.join(split)


def shift_data(raw_data, cols=5, shift=-3):
    '''Přenásobí hodnoty proudu o >shift< řádů (kompenzace děliče).'''
    a = raw_data.split(',')
    x_frequencies = {5: 2, 7: 3, 13: 3, 15: 4}
    freq = x_frequencies[cols]
    a[::freq] = [shift_number(c, shift) for c in a[::freq]]
    return ','.join(a)


inp = "+10.000E-06,+005.008E+00,+09.900E-06,+005.036E+00,+09.800E-06,+005.132E+00"
print(inp)
print(shift_data(inp, cols=5, shift=-3))

# +005.036E+00
