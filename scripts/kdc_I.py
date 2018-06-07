# -*- coding: utf-8 -*-
"""
Simple DC setting script
Measures U depending on I at a constant I.
Made for Honza Vaniš for biased measurements on Veeco Multimode.
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
make_sure_path_exists(folder)
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
    print(' Usage: python nmiv.py CURRENT name')
    sys.exit()  
if len(sys.argv) != 4:
    print('Not enough parameters supplied.')
    sys.exit()

# Try to load parameters into variables
try:
    current = float(sys.argv[1])
except:
    print("There was a problem converting the current parameter. \nMaybe you made a mistake?")
    sys.exit()

try:
    interval = float(sys.argv[2])
except:
    print("There was a problem converting the interval parameter. \nMaybe you made a mistake?")
    sys.exit()

try:
    name = str(sys.argv[3])
except:
    print("There was a problem converting provided name to string. \nMaybe you made a mistake?")
    sys.exit()
# -------------------------
mid = prefix+name
print('---------------------------------------------')

rm = visa.ResourceManager('C:\Windows\System32\\visa32.dll')
inst = rm.open_resource('GPIB0::17::INSTR')

inst.write("F1,0X")    # Source I, measure V, DC
inst.write("H0X")      # Immediate trigger

# Output format (source+measure, no prefix or suffix, one line of DC data per talk)
inst.write("G5,2,0X")

inst.write("B" + str(current) + ",0,0X")   # Bias current , auto range, no delay
inst.write("N1X")  # Operate



filename = folder+mid.replace(':', '.')
fallback_filename = fallback_folder+mid.replace(':', '.')
with open(filename+".txt", "w") as myfile:
    myfile.write("t [s] \t\t\t I [A] \t\t\t U[V]\n")
with open(fallback_filename+".txt", "w") as myfile:
    myfile.write("t [s] \t\t\t I [A] \t\t\t U[V]\n")

s = 0
#fig = plt.figure()
#ax = fig.add_subplot(1,1,1)
#plt.xlabel('Time (s)')
#plt.ylabel('Voltage (V)')
#plt.title('KDC, Constant I={} A'.format(current))
t, V = [], []
try:
    while True:
        line = inst.read()
        x, y = line.split(',')
        c = float(x)
        v = float(y)
        print("I = {:+.2E} A\t\tU = {:+9.3f} V".format(c, v))
        try:
            with open(filename+".txt", "a") as myfile:
                myfile.write("{}\t{:+.2E}\t{:+9.3f}\n".format(s, c, v))
        except:
            print('ERROR: Saving txt data on S:/ failed!!')
        with open(fallback_filename+".txt", "a") as myfile:
            myfile.write("{}\t{:+.2E}\t{:+9.3f}\n".format(s, c, v))

        t.append(s)
        V.append(v)
        #ax.clear()
        #ax.plot(t, V)
        #plt.show(block=False)
        #plt.pause(0.001)
        
        s += interval
        time.sleep(interval)
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
