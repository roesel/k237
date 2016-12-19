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

    cols = 0
    sweep_id = 0
    full_data = []
    negative_current = False
    log_sweep = True
    stop = True

    def __init__(self, dialog):
        Ui_sweepergui.__init__(self)
        self.setupUi(dialog)

        # Connect "add" button with a custom function (addInputTextToListbox)
        self.exportButton.clicked.connect(self.export_data)
        self.startBtn.clicked.connect(self.startFunc)
        self.logRadioButton.clicked.connect(self.switch_linear)
        self.linRadioButton.clicked.connect(self.switch_linear)

        # Populate comboBox
        self.decadeComboBox.clear()
        self.decadeComboBox.addItems(['5', '10', '25', '50'])
        self.decadeComboBox.setCurrentIndex(1)

        # Připojení k instrumentu
        #self.inst = Instrument('GPIB0::17::INSTR', visa_location='C:\WINDOWS\SysWOW64\\visa32.dll')
        self.inst = Instrument('GPIB0::17::INSTR', virtual=False)

    def artSleep(self, sleepTime):
        """
        Čeká čas sleepTime v eskundách, zatím ale každých 50 milisekund řeší
        akce, o které se někdo pokoušel v GUI.
        """
        stop_time = QtCore.QTime()
        stop_time.restart()
        while stop_time.elapsed() < sleepTime * 1000:
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
        ax1f1.set_title('Sweep @ ' + str(self.sweep_id))
        for d in data:
            x, y = d
            ax1f1.plot(x, y, color='red')
            if self.log_sweep:
                ax1f1.set_xscale('log')
            else:
                ax1f1.set_xscale('linear')
        self.rmmpl()
        self.addmpl(fig1)

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

    def validateInput(self, sw_min, sw_max, decade, delay, log_sweep, step):
        # Unit testing :P
        try:
            a = float(sw_min)
            a = float(sw_max)
            if not log_sweep:
                a = float(step)
        except:
            return False

        # Code
        if log_sweep:
            if (float(sw_min) > 0 and
                float(sw_max) > 0 and
                    float(sw_min) != float(sw_max)):
                return True
            else:
                return False
        else:
            # lin sweep
            if (float(sw_min) != float(sw_max) and
                    abs(float(sw_max) - float(sw_min)) > float(step)):
                return True
            else:
                return False

    def stopFunc(self):
        print('ABORT! Attempted to STOP sweep!')
        self.inst.operate(False)
        self.stop = True

    def startFunc(self):
        ''' Posbírá z GUI parametry a odpovídajícím způsobem přeloží.'''
        # vypnout ruční brzdu
        self.stop = False

        # aktuální čas pro ID
        self.sweep_id = datetime.datetime.now()

        sw_min = str(self.startEdit.text())
        sw_max = str(self.endEdit.text())
        step = str(self.stepEdit.text())
        delay = str(self.delaySpinBox.value())
        decade = str(self.decadeComboBox.currentIndex())
        n = self.pocetMereniBox.value()

        self.bigProgBar.setValue(0)
        self.bigProgBar.setMaximum(n)
        self.littleProgBar.setValue(0)

        log_sweep = self.logRadioButton.isChecked()
        lin_sweep = self.linRadioButton.isChecked()
        self.log_sweep = log_sweep

        col_source = self.sourceCheckBox.checkState()
        col_delay = self.delayCheckBox.checkState()
        col_measure = self.measureCheckBox.checkState()
        col_time = self.timeCheckBox.checkState()

        self.cols = 0
        if col_source:
            self.cols += 1
        if col_delay:
            self.cols += 2
        if col_measure:
            self.cols += 4
        if col_time:
            self.cols += 8

        if self.validateInput(sw_min, sw_max, decade, delay, log_sweep, step):
            self.measure(sw_min, sw_max, decade, delay, log_sweep, step, n)
        else:
            print('Input failed validation.')
            self.show_notification('failed_validation')

    def show_notification(self, code):
        if code == 'failed_validation':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Chybné parametry sweepu.")
            msg.setInformativeText("")
            msg.setWindowTitle("Sweeper - varování")
            msg.setDetailedText("TODO")
            msg.exec_()

    def measure(self, sw_min, sw_max, decade, delay, log_sweep, step, n):
        ''' Spustí měření s již validovanými parametry. '''
        # Disable UI
        self.enable_ui(False)

        # Declare Export not done on this sweep
        self.exportButton.setText('Export')

        # Úvodní stabilizace
        stabilize_time = self.stableSpinBox.value()
        self.stabilize(sw_min, stabilize_time)

        # Nastavení sweepu
        self.inst.set_source_and_function('I', 'Sweep')
        # Nastavení formátu dat
        self.inst.write("G" + str(self.cols) + ",2,2X")

        if self.log_sweep:
            self.inst.write("Q2," + sw_min + "," + sw_max + "," + decade + ",0," + delay + "X")
        else:
            self.inst.write("Q1," + sw_min + "," + sw_max + "," + step + ",0," + delay + "X")

        data = []
        self.full_data = []
        n_hotovych_mereni = 0
        for mereni in range(n):
            if self.stop:
                break
            output = self.run_sweep()
            if output:
                sweep_results = misc.nice_format(output, cols=self.cols)
                data.append(misc.unpack(sweep_results, cols=self.cols))
                self.full_data.append(sweep_results)
                n_hotovych_mereni += 1
                self.bigProgBar.setValue(n_hotovych_mereni)
                self.plot_data(data)
            else:
                print("Output was empty. Interrupted measurement?")

        self.inst.operate(False)
        self.enable_ui(True)
        self.plot_data(data)

    def run_sweep(self):
        ''' Provede jeden sweep, který už musí být definovaný ve stroji.
            Na konci 3 vteřiny spí, aby se mělo napětí čas ustálit před dalším měřením.

            Vrací string se všemi hodnotami sweepu.
        '''
        print('\nSpoustim sweep...')
        self.inst.write("U8X")
        out = self.inst.read()
        print('U8X -> ' + out)
        out = out.replace('\r', '').replace('\n', '')
        print("Out: {}".format(out))
        sweep_defined_size = int(out[-4:])
        print('Pocet bodu ve sweepu: ' + str(sweep_defined_size))

        self.littleProgBar.setValue(0)
        self.inst.trigger()     # Immediate trigger
        sweep_done = False
        while not sweep_done:
            if self.stop:
                break
            self.artSleep(0.2)
            self.inst.write("U11X")
            status = self.inst.read()
            if (status == 'SMS' + str(sweep_defined_size).zfill(4) + '\r\n'):
                sweep_done = True
            else:
                status_edit = status.replace('\r', '').replace('\n', '')
                try:
                    progress = int(status_edit[-4:])
                    self.littleProgBar.setValue(int(progress / sweep_defined_size * 100))
                except:
                    print('Invalid progress!')
        print('One sweep done.')
        self.littleProgBar.setValue(100)
        # print('Sleeping for 0.5 s...')
        # self.artSleep(0.5)
        if self.stop:
            return ""
        else:
            return self.inst.read()

    def stabilize(self, bias, stabilize_time):
        # Počáteční stabilizace
        self.inst.set_source_and_function('I', 'DC')
        self.inst.write("B" + bias + ",0,20X")
        self.inst.operate(True)
        self.inst.trigger()
        self.artSleep(stabilize_time)

    def switch_linear(self):
        log_sweep = self.logRadioButton.isChecked()
        lin_sweep = self.linRadioButton.isChecked()
        if log_sweep:
            self.stepEdit.setEnabled(False)
            self.decadeComboBox.setEnabled(True)
        else:
            self.decadeComboBox.setEnabled(False)
            self.stepEdit.setEnabled(True)

    def enable_ui(self, status):
        ui_elements = [
            self.startEdit,
            self.endEdit,
            self.stepEdit,
            self.delaySpinBox,
            self.decadeComboBox,
            self.pocetMereniBox,
            self.logRadioButton,
            self.linRadioButton,
            self.sourceCheckBox,
            self.delayCheckBox,
            self.measureCheckBox,
            self.timeCheckBox,
            self.stableSpinBox,
        ]

        for element in ui_elements:
            element.setEnabled(status)

        if status:
            self.switch_linear()

        if status:
            self.startBtn.clicked.disconnect()
            self.startBtn.clicked.connect(self.startFunc)
            self.startBtn.setText("Start")
        else:
            self.startBtn.clicked.disconnect()
            self.startBtn.clicked.connect(self.stopFunc)
            self.startBtn.setText("Abort")

    def export_data(self):
        """
        Exportuje data pomocí ukládacího dialogu Qt. V případě chybného zadání
        souboru nic neudělá a potěžuje si do konzole.
        """
        proposed_name = str(self.sweep_id).replace(" ", "_").replace(":", ".")

        # Qt Dialog na výběr souboru k uložení
        save_file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            'Exportovat výsledky měření',
            'C:\Repa\k237\data\sweep_' + proposed_name + '.txt',
            'Text Files (*.txt);;All Files (*)'
        )

        # Vlastní uložení souboru
        try:
            with open(save_file_name, "w") as text_file:
                text_file.write('# ======== Sweep ID: ' + str(self.sweep_id) + ' ========' + '\n')
                text_file.write(
                    '# ======== ' +
                    str(len(self.full_data)) + ' sweeps' +
                    ' ========' + '\n')

                for data in self.full_data:
                    text_file.write('# ======== SWEEP START ========\n')
                    text_file.write(data.replace(',', '    '))
                    text_file.write('# ======== SWEEP END ========\n\n')

            # Update GUI
            self.exportButton.setText('Export ✔')
        except:
            print("Export neúspěšný. Data pravděpodobně nejsou uložena!")

            # Update GUI
            self.exportButton.setText('Export ✗')
