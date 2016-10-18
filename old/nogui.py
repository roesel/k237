# -*- coding: utf-8 -*-
from k237 import Instrument
import time

inst = Instrument('GPIB0::17::INSTR', visa_location='C:\WINDOWS\SysWOW64\\visa32.dll')

sw_min = str(100e-12)      # minimum sweepu (od jaké hondoty)
sw_max = str(1e-12)        # maximum sweepu (po jakou hodnotu)

# Počáteční stabilizace
inst.set_source_and_function('I', 'DC')
inst.write("B"+sw_min+",0,20X")
inst.operate(True)
inst.trigger()
time.sleep(15)

# Nastavení sweepu
inst.set_source_and_function('I', 'Sweep')
inst.write("G5,2,2X")  # dvojka na konci znamená "všechny hodnoty sweepu najednou"
inst.write("Q2,"+sw_min+","+sw_max+",1,0,10X")
