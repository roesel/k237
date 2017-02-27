# -*- coding: utf-8 -*-
import numpy as np
from io import StringIO   # StringIO behaves like a file object


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
