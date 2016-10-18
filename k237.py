# -*- coding: utf-8 -*-

import time
import visa

class Instrument:
    'Třída obsluhující měřící přístroj KEITHLEY 237.'

    verbose = True

    # inst
    visa_location = ''
    resource_address = ''

    def __init__(self, resource_address, visa_location = False):
        self.resource_address = resource_address
        if visa_location:
            self.visa_location = visa_location
        self.initialize_communication()

    def initialize_communication(self):
        'Zahajuje komunikaci s přístrojem.'

        # Nastavení VISA knihovny
        if verbose:
            print('Nastavuji VISA knihovnu...')
        if visa_location:
            rm = visa.ResourceManager()
        else:
            rm = visa.ResourceManager(visa_location)

        # Připojení k přístroji na konkrétní adrese
        if verbose:
            print('Připojuji se k zařízení...')
        self.inst = rm.open_resource(resource_address)

    def set_source_and_function(self, source, function):
        # Nastavení zdroje napětí/proudu
        if source == 'V':
            source_num = '0'
        elif source == 'I':
            source_num = '1'
        else:
            raise ValueError('Invalid source specified. Valid options: V, I.')

        # Nastavení DC/sweep
        if function.lower() == 'dc':
            function_num = '0'
        elif function.lower() == 'sweep':
            function_num = '1'
        else:
            raise ValueError('Invalid function specified. Valid options: DC, Sweep.')

        # Odesílání nastavení zařízení
        self.inst('F'+source_num+','+function_num+'X')
