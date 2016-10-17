# -*- coding: utf-8 -*-
class Instrument:
    'Třída obsluhující měřící přístroj KEITHLEY 237.'
    resource_location = ''

    def __init__(self, resource_address, visa_location = False):
        self.resource_address = resource_address
        if visa_location:
            self.visa_location = visa_location

    def initialize_communication(self):


    def displayEmployee(self):
        print "Name : ", self.name,  ", Salary: ", self.salary
