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
        if self.verbose:
            print('Nastavuji VISA knihovnu...')
        if self.visa_location:
            rm = visa.ResourceManager(self.visa_location)
        else:
            rm = visa.ResourceManager()

        # Připojení k přístroji na konkrétní adrese
        if self.verbose:
            print('Pripojuji se k zarizeni...')
        self.inst = rm.open_resource(self.resource_address)

    def set_log_sweep(self, s_min, s_max, points=1, range=0, delay=20):
        ''' Nastaví sweep na přístroji, opět půjde vylepšit na chytřejší. '''
        self.inst.write('Q2,'+str(s_min)+","+str(s_max)+","+str(points)+','+str(range)+','+str(delay)+'X')

    def trigger(self):
        self.inst.write('H0X')

    def operate(self, on):
        if on:
            self.inst.write('N1X')
        else:
            self.inst.write('N0X')

    def write(self, command):
        self.inst.write(command)

    def read(self):
        return self.inst.read()

    def set_source_and_function(self, source, function):
        # Nastavení zdroje napětí/proudu
        if source.upper() == 'V':
            source_num = '0'
        elif source.upper() == 'I':
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

        if self.verbose:
            print('K237 bude zdroj '+source.upper()+' a merime v modu '+function.upper()+'.')

        # Odesílání nastavení zařízení
        self.inst.write('F'+source_num+','+function_num+'X')

    def set_data_format(self, items=5, form=2, lines=2):
        ''' Nastavuje formát, ale zatím není moc chytrá a vlastně nevím, jak ji
            chci udělat.
        '''
        self.inst.write('G'+str(items)+','+str(form)+','+str(lines)+'X')
