# -*- coding: utf-8 -*-
"""
Simple DC measuring script
Measures I depending on U
Made for testing nanomanipulator measurements with Stanislav.

Run in "activate py35_32" !!!
"""

import time
import visa
import datetime
import sys
import os
import errno
import numpy as np
import matplotlib.pyplot as plt


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# ------------------------
date = '{:%Y_%m_%d}'.format(datetime.datetime.now())
fallback_folder = 'C:/Users/tiagulskyi/Desktop/NMIV_data/'+date+'/'
folder = 'S:/Roesel/nmiv_data/'+date+'/'
try:
    make_sure_path_exists(folder)
    network = True
except:
    print("WARNING: Network unreachable, measurement will NOT save onto S:/ drive.")
    network = False
make_sure_path_exists(fallback_folder)
prefix = '{:%Y_%m_%d__%H:%M}_{}_'.format(datetime.datetime.now(), 'NMIV')
# ------------------------


def rollback():
    inst.write("N0X")  # Operate OFF
    inst.close()

# ------------------------
print('\n---------------------------------------------')
print(' NMIV - Nanomanipulator I-V measuring script  ')
print('---------------------------------------------')
# Input checking
# Check for number of parameters
if len(sys.argv) != 8:
    if sys.argv[1] == '--help':
        print(' Usage: python nmiv.py START_V STOP_V RETURN #_OF_POINTS #_OF_AVG DELAY[ms] NAME')
    else:
        print('Not enough parameters supplied.')
    sys.exit()

# Try to load parameters into variables
try:
    start_voltage = float(sys.argv[1])
    stop_voltage = float(sys.argv[2])
    there_and_back = int(sys.argv[3])
    number_of_points = int(sys.argv[4])
    avg_from = int(sys.argv[5])
    delay = int(sys.argv[6])
except:
    print("There was a problem converting some number parameters. \nMaybe you made a mistake?")
    sys.exit()

try:
    name = str(sys.argv[7])
except:
    print("There was a problem converting provided name to string. \nMaybe you made a mistake?")
    sys.exit()
# -------------------------

mid = prefix+name

if there_and_back:
    both_ways = "both ways"
else:
    both_ways = "one way"
def get_infostring():
    out = """ Measurement ID: {}
 Start:\t{} V
 Stop:\t{} V
 \# of points:\t{}
 Averaging {} measurements.
 Measuring {}.""".format(
        mid, start_voltage, stop_voltage, number_of_points, avg_from, both_ways)
    return out

print(get_infostring())
print('---------------------------------------------')



rm = visa.ResourceManager('C:\Windows\System32\\visa32.dll')
inst = rm.open_resource('GPIB0::17::INSTR')

inst.write("F0,0X")    # Source V, measure I, DC
inst.write("H0X")      # Immediate trigger

# Output format (source+measure, no prefix or suffix, one line of DC data per talk)
inst.write("G5,2,0X")

voltages = np.linspace(start_voltage, stop_voltage, num=number_of_points)
if there_and_back:
    voltages = np.append(voltages,voltages[::-1])

#print("Voltages are:\n{}".format(voltages))
currents = []
errs = []

try:
    inst.write("B" + str(voltages[0]) + ",0," + str(delay) + "X")   # Bias current , auto range, no delay
    inst.write("N1X")  # Operate
    # TODO Should we sleep here?
    for v in voltages:
        inst.write("B" + str(v) + ",0," + str(delay) + "X")   # Bias current , auto range, no delay
        # TODO Should we sleep here?
        data = []
        for i in range(avg_from):
            line = inst.read()
            x, y = line.split(',')
            data.append(float(y))
        npdata = np.array(data)
        avg = np.average(npdata)
        std = np.std(npdata)
        percent = int(100*std/avg)
        print("U = {:+9.3f}\tI = {:+.2E} +- {:+.2E} ({:4d} %) (out of {} points)".format(v, avg, std, percent, len(data)))
        currents.append(avg)
        errs.append(std)
except KeyboardInterrupt:
    # Handling ^C interrupt
    rollback()
except:
    # Emergency rollback (operate off)
    rollback()
    raise

# We are probably done, so rollback
#print("-------------------\nApplying negative voltage (-10 V)...")
#v = -10 # discharge volage
#inst.write("B" + str(v) + ",0,0X")
#for i in range(5):
#    _ = inst.read()
print("-----\nMeasurement should be done, turning OFF operate...")
rollback()
print("-----\nSaving data...")
filename = folder+mid.replace(':', '.')
fallback_filename = fallback_folder+mid.replace(':', '.')
data_out = np.stack([voltages, currents], axis=1)
if network:
    try:
        np.savetxt(filename+'.txt', data_out, header=get_infostring()+'\nU [V] \t\t\t I[A]', fmt='%.7e')
    except:
        print('ERROR: Saving txt data on S:/ failed!!')
np.savetxt(fallback_filename+'.txt', data_out, header=get_infostring()+'\nU [V] \t\t\t I[A]', fmt='%.7e')

print("-----\nPlotting and saving plot...")
fig = plt.figure(1)
plt.errorbar(voltages, currents, yerr=errs, marker="o", linestyle="None",
             capsize=2, elinewidth=1, markeredgewidth=1, ecolor='r')
#plt.xlim([min_voltage, max_voltage])
plt.xlabel('U [V]')
plt.ylabel('I [A]')
plt.title(mid)

try:
    plt.savefig(filename+'.png', dpi=200)
except:
    print('ERROR: Saving image on S:/ failed!!')

plt.savefig(fallback_filename+'.png', dpi=200)

plt.show()
print("----- DONE")












#end
