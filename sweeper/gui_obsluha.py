# -*- coding: utf-8 -*-
import sys
import time
import datetime
import misc
from PyQt5 import QtCore, QtGui, QtWidgets

from gui import Ui_sweepergui
from k237 import Instrument

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)


class GuiProgram(Ui_sweepergui):

    instrument_configured = False
    pocet_bodu = 0

    def __init__(self, dialog):
        Ui_sweepergui.__init__(self)
        self.setupUi(dialog)

        # Connect "add" button with a custom function (addInputTextToListbox)
        #self.addBtn.clicked.connect(self.plot_figure)
        self.startBtn.clicked.connect(self.startFunc)

        # Populate comboBox
        self.decadeComboBox.clear()
        self.decadeComboBox.addItems(['5', '10', '25', '50'])
        self.decadeComboBox.setCurrentIndex(1)

        # Připojení k instrumentu
        self.inst = Instrument('GPIB0::17::INSTR', visa_location='C:\WINDOWS\SysWOW64\\visa32.dll')

    def artSleep(self, sleepTime):
        stop_time = QtCore.QTime()
        stop_time.restart()
        while stop_time.elapsed() < sleepTime:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 50)

    def plot_figure(self):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.plot(np.random.rand(5))
        self.rmmpl()
        self.addmpl(fig1)

    def plot_data(self, data):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.set_xlabel('I [A]')
        ax1f1.set_ylabel('U [V]')
        ax1f1.set_title('Sweep @ '+str(datetime.datetime.now()))
        for d in data:
            x, y = d
            ax1f1.semilogx(x, y, color='red')
        self.rmmpl()
        self.addmpl(fig1)

    # def addInputTextToListbox(self):
    #     txt = self.myTextInput.text()
    #     self.mplfigs.addItem(txt)

    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                self.mplwindow, coordinates=True)
        self.mplvl.addWidget(self.toolbar)

    def rmmpl(self,):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()

    def startFunc(self):
        # Parametry sweepu, časem načíst z GUI
        #sw_min = str(100e-12)      # minimum sweepu (od jaké hondoty)
        #sw_max = str(1e-12)        # maximum sweepu (po jakou hodnotu)
        sw_min = str(self.startEdit.text())
        sw_max = str(self.endEdit.text())
        delay = str(self.delaySpinBox.value())
        decade = str(self.decadeComboBox.currentIndex())
        n = self.pocetMereniBox.value()

        self.bigProgBar.setValue(0)
        self.bigProgBar.setMaximum(n)
        self.littleProgBar.setValue(0)

        # Úvodní stabilizace
        stabilize_time = self.stableSpinBox.value()
        self.stabilize(sw_min, stabilize_time)

        # Nastavení sweepu
        self.inst.set_source_and_function('I', 'Sweep')
        self.inst.write("G5,2,2X")
        self.inst.write("Q2,"+sw_min+","+sw_max+","+decade+",0,"+delay+"X")

        data = []
        n_hotovych_mereni = 0
        for mereni in range(n):
            sweep_results = misc.nice_format(self.run_sweep())
            data.append(misc.unpack(sweep_results))
            n_hotovych_mereni += 1
            self.bigProgBar.setValue(n_hotovych_mereni)

        self.inst.operate(False)
        self.plot_data(data)


    def run_sweep(self):
        ''' Provede jeden sweep, který už musí být definovaný ve stroji.
            Na konci 3 vteřiny spí, aby se mělo napětí čas ustálit před dalším měřením.
            POZOR: Podmínka na ukončení while-cyklu je natvrdo "21 měření". Pokud
            se změní nastavení sweepu (Q...X), tak může skončit dřív a nebo neskončit vůbec.

            Vrací string se všemi hodnotami sweepu.
        '''
        print('\nSpoustim sweep...')
        self.inst.write("U8X")
        out = self.inst.read()
        print('U8X -> '+out)
        out = out.replace('\r', '').replace('\n', '')
        sweep_defined_size = int(out[-4:])
        print('Pocet bodu ve sweepu: '+str(sweep_defined_size))

        self.littleProgBar.setValue(0)
        self.inst.trigger()     # Immediate trigger
        sweep_done = False
        while not sweep_done:
            self.artSleep(0.2)
            self.inst.write("U11X")
            status = self.inst.read()
            if (status == 'SMS'+str(sweep_defined_size).zfill(4)+'\r\n'):
                sweep_done = True
            else:
                status_edit = status.replace('\r', '').replace('\n', '')
                progress = int(status_edit[-4:])
                self.littleProgBar.setValue(int(progress/sweep_defined_size*100))
        print('Done.')
        self.littleProgBar.setValue(100)
        print('Sleeping for 3s...')
        self.artSleep(3)
        return self.inst.read()

    def stabilize(self, bias, stabilize_time):
        # Počáteční stabilizace
        self.inst.set_source_and_function('I', 'DC')
        self.inst.write("B"+bias+",0,20X")
        self.inst.operate(True)
        self.inst.trigger()
        self.artSleep(stabilize_time)
