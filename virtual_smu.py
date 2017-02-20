# -*- coding: utf-8 -*-
import numpy as np
import time
from random import randint


class Virtual_SMU:
    'Třída obsluhující virtuální přístroj na testování.'
    sweep_running = False
    sweep_n = 0
    sweep_len = 0
    data = ""
    stack = ""

    def __init__(self):
        print("SMU je virtualni. Vysledky se mohou a budou lisit od realneho pristroje.")

    def read(self):
        out_stack = self.stack

        if self.sweep_n == self.sweep_len:
            print("Loading DATA for next read!")
            self.stack = self.data
            self.data = ""
            self.sweep_n = 0

        print("read() returned: {}".format(out_stack))
        return out_stack

    def write(self, in_command):
        print("Written: {}".format(in_command))
        in_command = in_command.replace('\r', '').replace('\n', '')
        if in_command[0:2] == "Q1":
            expl = in_command.split(',')
            sweep_min = float(expl[1])
            sweep_max = float(expl[2])
            sweep_step = float(expl[3])
            points = np.arange(sweep_max, sweep_min, sweep_step)
            print("Lenght of sweep: {}".format(len(points)))
            self.sweep_len = len(points)
            self.points = points
        elif in_command[0:3] == "U8X":
            response = 'SWEEP' + str(self.sweep_len).zfill(4) + '\r\n'
            print("Response: {}".format(response))
            self.stack = response
        elif in_command[0:4] == "U11X":
            self.increase_sweep_counter()
            self.stack = 'SMS' + str(self.sweep_n).zfill(4) + '\r\n'
        elif in_command[0:3] == "N0X":
            self.sweep_n = 0
            self.sweep_len = 0

    def increase_sweep_counter(self):
        x_data = "{:.4E}".format(self.points[self.sweep_n])

        self.sweep_n += 1

        self.data += x_data + ",+000.{}E+00,".format(randint(100, 999))
        time.sleep(0.1)
