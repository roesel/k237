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
from io import StringIO


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
if len(sys.argv) != 9:
    try:
        if sys.argv[1] == '--help':
            print(' Usage: python nmiv_sweep.py START_V STOP_V NEGATIVE #_OF_POINTS[0-3] RETURN RANGE[0-4] DELAY NAME')
        else:
            print('Not enough parameters supplied.')
    except:
        print('Not enough parameters supplied. \nTry running the program with --help.')
    sys.exit()

# Try to load parameters into variables
try:
    start_voltage = float(sys.argv[1])
    stop_voltage = float(sys.argv[2])
    negative = int(sys.argv[3])
    number_of_points = int(sys.argv[4])
    there_and_back = int(sys.argv[5])
    rng = int(sys.argv[6])
    delay = int(sys.argv[7])
except:
    print("There was a problem converting some number parameters. \nMaybe you made a mistake?")
    sys.exit()

try:
    name = str(sys.argv[8])
except:
    print("There was a problem converting provided name to string. \nMaybe you made a mistake?")
    sys.exit()
# -------------------------
print(there_and_back)
mid = prefix+name
if negative:
    start_voltage = start_voltage*-1
    stop_voltage = stop_voltage*-1
def get_infostring():
    points_translation = [5,10,25,50]
    range_translation = ['Auto', '1.1 V', '11 V', '110 V', '1100 V']
    ways_translation = ['one way', 'both ways']
    out = """ ID:\t\t{}
 Mode:\t\tLog Sweep
 Start:\t\t{} V
 Stop:\t\t{} V
 Points/decade:\t{} ({})
 Range:\t\t{} ({})
 Measuring {}. ({})""".format(
        mid, start_voltage, stop_voltage,
        points_translation[number_of_points], number_of_points,
        range_translation[rng], rng,
        ways_translation[there_and_back], there_and_back)
    return out

print(get_infostring())
print('---------------------------------------------')



rm = visa.ResourceManager('C:\Windows\System32\\visa32.dll')
inst = rm.open_resource('GPIB0::17::INSTR')
# Source V, measure I, Sweep
inst.write("F0,1X")    
# Output format (source+measure, no prefix or suffix, all lines of DC data per talk)
inst.write("G5,2,2X")
# Create sweep list
sweep_command = "Q2,{},{},{},{},{}X".format(start_voltage, stop_voltage, number_of_points, rng, delay)
print(sweep_command)
inst.write(sweep_command)
# If looping, append sweep
if there_and_back:
    sweep_append = "Q8,{},{},{},{},{}X".format(stop_voltage, start_voltage, number_of_points, rng, delay)
    inst.write(sweep_append) 

inst.write("U8X") 
out = inst.read() 
#print('U8X -> ' + out) 
out = out.replace('\r', '').replace('\n', '') 
#print("Out: {}".format(out)) 
sweep_defined_size = int(out[-4:]) 
print('Number of points in sweep: ' + str(sweep_defined_size)) 

inst.write("N1X")  # Operate
inst.write('H0X')  # Trigger

data = ""
try:
    sweep_done = False 
    while not sweep_done: 
        time.sleep(0.2) 
        inst.write("U11X") 
        status = inst.read() 
        if (status == 'SMS' + str(sweep_defined_size).zfill(4) + '\r\n'):
            sweep_done = True
            status_edit = status.replace('\r', '').replace('\n', '')
            progress = int(status_edit[-4:]) 
            print('Sweep progress: {}/{}\t({} %)'.format(progress, sweep_defined_size, (int(progress / sweep_defined_size * 100)))) 
        else: 
            status_edit = status.replace('\r', '').replace('\n', '') 
            try: 
                progress = int(status_edit[-4:]) 
                print('Sweep progress: {}/{}\t({} %)'.format(progress, sweep_defined_size, (int(progress / sweep_defined_size * 100)))) 
            except: 
                print('Invalid sweep progress?')
    output = inst.read()
    sweep_results = nice_format(output) 
    unpacked_results = unpack(sweep_results) 

except KeyboardInterrupt:
    # Handling ^C interrupt
    rollback()
except:
    # Emergency rollback (operate off)
    rollback()
    raise

#print(output)
#print('-----')
#print(sweep_results)
#print('-----')
#print(unpacked_results)

#print("U = {:+9.3f}\tI = {:+.2E} +- {:+.2E} ({:4d} %) (out of {} points)".format(v, avg, std, percent, len(data)))


print("-----\nMeasurement should be done, turning OFF operate...")
rollback()

print("-----\nSaving data...")
filename = folder+mid.replace(':', '.')
fallback_filename = fallback_folder+mid.replace(':', '.')
data_out = np.array(unpacked_results)
data_out = np.transpose(data_out)
try:
    np.savetxt(filename+'.txt', data_out, header=get_infostring()+'\nU [V] \t\t\t I[A]', fmt='%.7e')
except:
    print('ERROR: Saving txt data on S:/ failed!!')
np.savetxt(fallback_filename+'.txt', data_out, header=get_infostring()+'\nU [V] \t\t\t I[A]', fmt='%.7e')

print("-----\nPlotting and saving plot...")
fig = plt.figure(1)
x, y = unpacked_results
if negative:
    x, y = -x, -y
if (not (y > 0).all()):
    print('WARNING: Some values are < 0, plot will not show all points!') 
plt.loglog(x, y, marker="o", linestyle="None")
#plt.xlim([min_voltage, max_voltage])
if negative:
    plt.xlabel('-U [V]')
    plt.ylabel('-I [A]')
else:
    plt.xlabel('U [V]')
    plt.ylabel('I [A]')
plt.title(mid)
plt.tight_layout()

try:
    plt.savefig(filename+'.png', dpi=200)
except:
    print('ERROR: Saving image on S:/ failed!!')

plt.savefig(fallback_filename+'.png', dpi=200)

plt.show()
print("----- DONE")












#end
