# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 11:15:36 2016

@author: roese
"""

import time



import visa
rm = visa.ResourceManager('C:\WINDOWS\SysWOW64\\visa32.dll')
#print(rm.list_resources())
#print(rm)
print('\n')
print('Setting instrument...\n')
inst = rm.open_resource('GPIB0::17::INSTR')
#print('Sending: *IDN? ...\n')
#print(inst.query('*IDN?'))


print(inst.write("F1,0X"))    # Source I, measure V, DC
inst.write("H0X")                                   # Immediate trigger
inst.write("G5,2,0X")
#current = 0.00000000001  # mA
current = 10e-12
inst.write("B" +str(current) +",0,0X")   # Bias current , auto range, no delay
inst.write("N1X")

start = time.time()

num_measurements = 20
for i in range(num_measurements):
    print(inst.read())


end = time.time()
diff = end - start
print(diff, " s")
print(diff/num_measurements, " s/meas")



#IDDC
