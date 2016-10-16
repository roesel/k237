# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 11:15:36 2016

@author: roese
"""

import time       # na sleep a stopování jak dlouho trvají operace

import visa       # import pyVISA

# ruční nastavení VISA knihovny (často není nutné)
rm = visa.ResourceManager('C:\WINDOWS\SysWOW64\\visa32.dll')

#print(rm.list_resources())       # print seznamu připojených zařízení

print('\n')
print('Setting instrument...\n')

# nastavení s jakým zařízením pracujeme
inst = rm.open_resource('GPIB0::17::INSTR')

# zadost o print identifikace zařízení
#print('Sending: *IDN? ...\n')
#print(inst.query('*IDN?'))

# nastavení - zdroj: proudu/napětí, měříme: proud/napětí, druh: DC/sweep
inst.write("F1,1X")    # Source I, measure V, Sweep

# nastavení v jakém formátu vrací přístroj data
inst.write("G5,2,2X")  # dvojka na konci znamená "všechny hodnoty sweepu najednou"

sw_min = str(1e-12)      # minimum sweepu (od jaké hondoty)
sw_max = str(100e-12)    # maximum sweepu (po jakou hodnotu)

# nahrání parametrů sweepu do zařízení (odpovídá čudlíku CREATE a jeho nastavení)
# pozor, nevím jak nastavovat parametr BIAS u swepu - to umím jen přímo na stroji mechanicky
inst.write("Q2,"+sw_min+","+sw_max+",1,0,10X")

def run_sweep():
    ''' Provede jeden sweep, který už musí být deifnovaný ve stroji.
        Na konci 3 vteřiny spí, aby se mělo napětí čas ustálit před dalším měřením.
        POZOR: Podmínka na ukončení while-cyklu je natvrdo "21 měření". Pokud
        se změní nastavení sweepu (Q...X), tak může skončit dřív a nebo neskončit vůbec.

        Vrací string se všemi hodnotami sweepu.
    '''
    print('\nRunning sweep...')
    inst.write("H0X")     # Immediate trigger
    sweep_done = False
    while not sweep_done:
        time.sleep(0.1)
        inst.write("U11X")
        if (inst.read()=='SMS0021\r\n'):
            sweep_done = True
    print('Done.')
    print('Sleeping for 3s...')
    time.sleep(3)
    return inst.read()


def plot_sweep(raw_data):
    ''' Tahle funkce by se měla rozdělit do více funkcí:
            * Zpracuje data co vrátil stroj
            * Oddělí 'x' a 'y'
            * Vykreslí graf
            * Přidá data na konec výstupního souboru

        POZOR, natvrdo zavedené "n_columns" - počet sloupců co vrací stroj.
        Může se rozbít pokud nastavíme jiný fomrát (G...X)
    '''
    raw_data = raw_data.replace('\r\n', '\n')
    spl = raw_data.split(',')
    n_columns = 2
    # tahle prasárna nahradí každou n-tou (druhou) čárku ENTERem (aby se oddělily řádky)
    data = "\n".join([",".join(spl[i:i+n_columns]) for i in range(0,len(spl),n_columns)])

    # funkce co udělá ze stringu "jakoby" soubor, aby ho mohlo našíst numpy jako ze souboru
    c = StringIO(data)
    x, y = np.loadtxt(c, delimiter=',', unpack = True)

    # vynesení do grafu s logaritmickým X
    plt.semilogx(x, y, color='red')

    # zapsání dat na konec výstupního souboru
    with open("sweep_data.txt", "a") as text_file:
        text_file.write('======== SWEEP START ========\n')
        text_file.write(data)
        text_file.write('======== SWEEP END ========\n\n')

    return x, y



import numpy as np
from io import StringIO   # StringIO behaves like a file object
import matplotlib.pyplot as plt

# vytvoření grafu
fig = plt.figure(1)
plt.clf()
plt.xlabel('I [A]')
plt.ylabel('U [V]')

ys = []       # drží y z více měření na závěrečné průměrování

# range určuje kolik VA charakteristik se bude dělat za sebou
for i in range(6):
    raw_data = run_sweep()
    x, y = plot_sweep(raw_data)
    ys.append(y)    # přidání napětí z aktuální charakteristiky do seznamu

# průměrování
avg = np.mean(np.array(ys), axis=0)
# vynesení křivky do grafu
plt.semilogx(x, avg, color='blue')


