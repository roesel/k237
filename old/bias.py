# -*- coding: utf-8 -*-
"""
Simple DC measuring script
"""

import time
import visa
import datetime
import sys

import numpy as np
import matplotlib.pyplot as plt

show_plot = True
if len(sys.argv) in [2, 3]:
    current = sys.argv[1]
    try:
        current = float(current)
    except:
        print('Current in wrong format. Exiting.')
        sys.exit()

    if len(sys.argv) == 3:
        if sys.argv[2] == "--no-plot":
            show_plot = False

else:
    print('Wrong arguments provided. Exiting.')
    sys.exit()

rm = visa.ResourceManager('C:\WINDOWS\SysWOW64\\visa32.dll')
# print(rm.list_resources())

inst = rm.open_resource('GPIB0::17::INSTR')
# print('Sending: *IDN? ...\n')
# print(inst.query('*IDN?'))

inst.write("F1,0X")    # Source I, measure V, DC
inst.write("H0X")                                   # Immediate trigger
# Output format (source+measure, no prefix or suffix, one line of DC data per talk)
inst.write("G5,2,0X")

inst.write("B" + str(current) + ",0,0X")   # Bias current , auto range, no delay
inst.write("N1X")  # Operate

if show_plot:
    fig = plt.figure(1)
    plt.ion()


start = time.time()

t_data = []
y_data = []
num_measurements = 0

folder = 'C:/Users/roese/Desktop/noise_data/'
mid = '{:%Y_%m_%d-%H%M}-{}'.format(datetime.datetime.now(), current)


def init_file():
    with open(folder + mid + '.txt', mode='w', encoding='utf-8') as outfile:
        outfile.write(
            'Measurement started on {:%d. %b %Y, %H:%M} at current {:.2E} A.\n-----\n'.format(datetime.datetime.now(), current))


def add_to_file(value):
    with open(folder + mid + '.txt', mode='a', encoding='utf-8') as outfile:
        addition = '\n'.join(str(x) for x in value) + '\n'
        outfile.write(addition)


def prettytime(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def get_stats(data):
    print('\n')
    print("\nBegin Stats -----------")

    if len(data) > 100:
        a = np.array(data)[100:]
        print("Avg: {:.3E} A".format(np.average(a)))
        print("Std: {:.3E} A".format(np.std(a)))
        print("Stdp: {} %\n".format(int(10000 * np.std(a) / np.average(a)) / 100))

    else:
        print('(Measurement not long enough for averaging.)')

    end = time.time()
    diff = end - start
    print('Elapsed time: ' + prettytime(diff) + '.')
    print('Each value took {:.2f} s.'.format(diff / num_measurements))
    print('Measurement frequency: {:.2f} meas/s.'.format(num_measurements / diff))
    print("End Stats -------------\n")


def rollback():
    inst.write("N0X")  # Operate OFF
    inst.close()


init_file()

save_freq = 10
try:
    limit = 100
    i = 0
    while i < limit:
        i += 1
        line = inst.read()
        x, y = line.split(',')
        t_data.append((time.time() - start))
        y_data.append(float(y))
        num_measurements += 1
        if show_plot:
            plt.cla()
            plt.plot(t_data, y_data)
            plt.title(mid)
            plt.xlabel('t [s]')
            plt.ylabel('U [V]')
            plt.draw()
            if num_measurements % 100 == 0:
                plt.savefig(folder + mid + '.png')
            plt.pause(0.01)
        if num_measurements % save_freq == 0:
            add_to_file(y_data[-save_freq:])
    print('100!')
    rollback()
    get_stats(y_data)

except KeyboardInterrupt:
    rollback()
    get_stats(y_data)
except:
    rollback()
    get_stats(y_data)
    raise
