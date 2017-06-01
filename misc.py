# -*- coding: utf-8 -*-
import numpy as np
from io import StringIO   # StringIO behaves like a file object


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


def nice_format(raw_data, cols=5):
    '''Zpracuje data co vrátil stroj.'''
    raw_data = raw_data.replace('\r\n', '\n')
    spl = raw_data.split(',')

    # TODO improve (generalize)
    sum_dict = {15: 4, 13: 3, 7: 3, 5: 2}

    n_columns = sum_dict[cols]
    # tahle prasárna nahradí každou n-tou (druhou) čárku ENTERem (aby se oddělily řádky)
    data = "\n".join([",".join(spl[i:i + n_columns]) for i in range(0, len(spl), n_columns)])

    return data


def unpack(data, cols=5):
    '''Zpracuje nice_format(data) do x,y sloupců na plotting.'''
    # funkce co udělá ze stringu "jakoby" soubor, aby ho mohlo našíst numpy jako ze souboru
    c = StringIO(data)
    if cols == 5:
        x, y = np.loadtxt(c, delimiter=',', unpack=True)
    elif cols == 15:
        x, d, y, t = np.loadtxt(c, delimiter=',', unpack=True)
    elif cols == 7:
        x, d, y = np.loadtxt(c, delimiter=',', unpack=True)
    elif cols == 13:
        x, y, t = np.loadtxt(c, delimiter=',', unpack=True)
    else:
        print('This format is not handled!')
        x, y = [], []

    return x, y


def append_output_file(data):
    '''Pravděpodobně se dá smazat.'''
    # zapsání dat na konec výstupního souboru
    with open("sweep_data.txt", "a") as text_file:
        text_file.write('======== SWEEP START ========\n')
        text_file.write(data)
        text_file.write('======== SWEEP END ========\n\n')


def pack_data(backpack, data):
    '''Vezme >data< a přidá je na konec >backpack<.'''
    x, y = data
    if len(backpack) > 0:
        return np.vstack((backpack.T, y)).T
    else:
        return np.vstack((x, y)).T


def get_range_number(sw_min, sw_max):
    '''Returns source range number for I-source as per page 65 of the Quick reference guide.'''
    range_number = 0
    a = max(abs(sw_min), abs(sw_max))
    if a < 1e-9:
        range_number = 1
    elif a < 1e-8:
        range_number = 2
    elif a < 1e-7:
        range_number = 3
    elif a < 1e-6:
        range_number = 4
    elif a < 1e-5:
        range_number = 5
    elif a < 1e-4:
        range_number = 6
    elif a < 1e-3:
        range_number = 7
    elif a < 1e-2:
        range_number = 8
    elif a < 1e-1:
        range_number = 9
    else:
        range_number = 0

    return range_number


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
