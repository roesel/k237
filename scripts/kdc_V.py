# -*- coding: utf-8 -*-
"""
Simple DC setting script
Measures I depending on U at a constant U.
Made for Stanislav for biased measurements on the SEM.
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
prefix = '{:%Y_%m_%d__%H:%M}_{}_'.format(datetime.datetime.now(), 'KDC')
# ------------------------

def rollback():
    inst.write("N0X")  # Operate OFF
    inst.close()

# ------------------------
print('\n---------------------------------------------')
print(' KDC - Keithley DC (mini)script  ')
print(' Not tested. Proceed with caution.')
print('---------------------------------------------')
# Input checking
# Check for number of parameters
if sys.argv[1] == '--help':
    print(' Usage: python nmiv.py VOLTAGE name')
    sys.exit()
if len(sys.argv) != 3:
    print('Not enough parameters supplied.')
    sys.exit()

# Try to load parameters into variables
try:
    voltage = float(sys.argv[1])
except:
    print("There was a problem converting the voltage parameter. \nMaybe you made a mistake?")
    sys.exit()

try:
    name = str(sys.argv[2])
except:
    print("There was a problem converting provided name to string. \nMaybe you made a mistake?")
    sys.exit()
# -------------------------
mid = prefix+name
print('---------------------------------------------')

rm = visa.ResourceManager('C:\Windows\System32\\visa32.dll')
inst = rm.open_resource('GPIB0::17::INSTR')

inst.write("F0,0X")    # Source V, measure I, DC
inst.write("H0X")      # Immediate trigger

# Output format (source+measure, no prefix or suffix, one line of DC data per talk)
inst.write("G5,2,0X")

inst.write("B" + str(voltage) + ",0,0X")   # Bias current , auto range, no delay
inst.write("N1X")  # Operate



filename = folder+mid.replace(':', '.')
fallback_filename = fallback_folder+mid.replace(':', '.')
with open(filename+".txt", "w") as myfile:
    myfile.write("t [s] \t\t\t U [V] \t\t\t I[A]\n")
with open(fallback_filename+".txt", "w") as myfile:
    myfile.write("t [s] \t\t\t U [V] \t\t\t I[A]\n")

s = 0
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
plt.xlabel('Time (s)')
plt.ylabel('Current (A)')
plt.title('KDC, Constant U={} V'.format(voltage))
t, I = [], []
try:
    while True:
        line = inst.read()
        x, y = line.split(',')
        vol = float(x)
        cur = float(y)
        print("U = {:+9.3f} V\t\tI = {:+.2E} A".format(vol, cur))
        if network:
            try:
                with open(filename+".txt", "a") as myfile:
                    myfile.write("{}\t{:+9.3f}\t{:+.2E}\n".format(s, vol, cur))
            except:
                print('ERROR: Saving txt data on S:/ failed!!')
        with open(fallback_filename+".txt", "a") as myfile:
            myfile.write("{}\t{:+9.3f}\t{:+.2E}\n".format(s, vol, cur))

        t.append(s)
        I.append(cur)
        ax.clear()
        ax.plot(t, I)
        plt.show(block=False)
        plt.pause(0.001)

        s += 1
        time.sleep(1)
except KeyboardInterrupt:
    # Handling ^C interrupt
    print('---------------------------------------------')
    print("Program iterrupted by user...")
    rollback()
except:
    # Emergency rollback (operate off)
    print('---------------------------------------------')
    print("Program encountered uncaught error... quitting...")
    rollback()
    raise
print('---------------------------------------------')
print("----- DONE")
