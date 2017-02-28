# -*- coding: utf-8 -*-
import time
import visa
from virtual_smu import Virtual_SMU

# TODO - u nastavování parametrů přístroje by mělo jít ověřit, zda se to
# povedlo a pokud ne, hodit chybu


class Instrument:
    'Třída obsluhující měřící přístroj KEITHLEY 237.'

    verbose = True           # Má program blábolit?
    visa_location = ''       # Umístění VISA knihovny
    virtual = False
    resource_address = ''    # Adresa měřáku (...GPIB::17...)
    SMU = None

    def __init__(self, resource_address, visa_location=False, virtual=False):
        '''
        Metoda volaná při tvorbě objektu.
        '''
        # Uložení adresy přístroje do vlastní proměnné
        self.resource_address = resource_address
        self.virtual = virtual

        # Pokud v parametrech bylo speciální umístění VISA knihovny, uložit do vlastní proměnné.
        if visa_location:
            self.visa_location = visa_location

        # Zahájit komunikaci s přístrojem
        self.initialize_communication()

    def initialize_communication(self):
        '''Zahajuje komunikaci s přístrojem.'''

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

        if not self.virtual:
            self.SMU = rm.open_resource(self.resource_address)
        else:
            self.SMU = Virtual_SMU()

        # V tuhle chvíli by mělo být všechno ready na měření.

    def trigger(self):
        '''
        Pošle na přístroj okamžitý trigger.
        '''
        self.SMU.write('H0X')

    def operate(self, on):
        '''
        Podle toho jestli on=True nebo on=False vypne/zapne OPERATE.
        '''
        if on:
            self.SMU.write('N1X')
        else:
            self.SMU.write('N0X')

    def write(self, command):
        '''
        Přepošle string do metody write našeho SMU.
        '''
        self.SMU.write(command)

    def read(self):
        '''
        Přečte .read() z SMU.
        '''
        return self.SMU.read()

    def read_lines(self):
        out = ""
        for i in range(1000):
            out += self.SMU.read() + "\n"
        return out

    def set_source_and_function(self, source, function):
        '''
        Čitelnější nastavení zdroje/měřené veličiny.
        '''
        # Nastavení zdroje napětí/proudu
        if source.upper() == 'U':
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
            print('K237 bude zdroj ' + source.upper() + ' a merime v modu ' + function.upper() + '.')

        # Odesílání nastavení zařízení
        self.SMU.write('F' + source_num + ',' + function_num + 'X')
