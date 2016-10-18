# -*- coding: utf-8 -*-
import numpy as np
from io import StringIO   # StringIO behaves like a file object

def nice_format(raw_data, n_columns=2):
    '''Zpracuje data co vrátil stroj.'''
    raw_data = raw_data.replace('\r\n', '\n')
    spl = raw_data.split(',')
    n_columns = 2
    # tahle prasárna nahradí každou n-tou (druhou) čárku ENTERem (aby se oddělily řádky)
    data = "\n".join([",".join(spl[i:i+n_columns]) for i in range(0,len(spl),n_columns)])

    return data

def unpack(data):
    '''Zpracuje nice_format(data) do x,y sloupců na plotting.'''
    # funkce co udělá ze stringu "jakoby" soubor, aby ho mohlo našíst numpy jako ze souboru
    c = StringIO(data)
    x, y = np.loadtxt(c, delimiter=',', unpack = True)
    return x, y

def append_output_file(data):
    # zapsání dat na konec výstupního souboru
    with open("sweep_data.txt", "a") as text_file:
        text_file.write('======== SWEEP START ========\n')
        text_file.write(data)
        text_file.write('======== SWEEP END ========\n\n')
