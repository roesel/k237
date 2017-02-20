# -*- coding: utf-8 -*-
import sys
import time
import datetime
import misc
import pickle
from PyQt5 import QtCore, QtGui, QtWidgets

from gui import Ui_sweepergui
from k237 import Instrument

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
#matplotlib.rcParams['savefig.directory'] = '/home/david/anaconda'
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
    decade_combo_values = ['5', '10', '25', '50']

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
        self.decadeComboBox.addItems(self.decade_combo_values)
        self.decadeComboBox.setCurrentIndex(1)

        # Try to load last parameters from Pickle
        self.load_parameters()

        # Připojení k instrumentu
        #self.inst = Instrument('GPIB0::17::INSTR', visa_location='C:\WINDOWS\SysWOW64\\visa32.dll')
        self.inst = Instrument('GPIB0::17::INSTR', virtual=False)

    def artSleep(self, sleepTime):
        """
        Čeká čas sleepTime v sekundách, zatím ale každých 50 milisekund řeší
        akce, o které se někdo pokoušel v GUI.
        """
        stop_time = QtCore.QTime()
        stop_time.restart()
        while stop_time.elapsed() < sleepTime * 1000:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 50)

    def plot_data(self, data):
        ''' Plots the provided data onto the figure in the GUI. '''

        original_xlim = self.ax.get_xlim()
        original_ylim = self.ax.get_ylim()

        self.ax.clear()  # Clear contents of current axis

        # Plot cosmetics
        self.ax.set_xlabel('I [A]')
        self.ax.set_ylabel('U [V]')
        self.ax.set_title('Sweep ID: ' + self.sweep_id)

        for i in range(len(data)):
            x, y = data[i]
            if i == len(data) - 1:
                color = '#0066FF'
            elif i == len(data) - 2:
                color = '#6600CC'
            else:
                color = '#FF0000'
            self.ax.plot(x, y, color=color)
            if self.log_sweep:
                self.ax.set_xscale('log')
            else:
                self.ax.set_xscale('linear')

            if i != 0 and self.chkLockRange.checkState():
                self.ax.set_xlim(original_xlim)
                self.ax.set_ylim(original_ylim)

        self.canvas.draw()  # Propagate changes to GUI

    def put_figure_into_gui(self, fig, ax):
        ''' Creates a figure and places it inside the GUI container. '''

        # Figure
        self.fig = fig
        self.ax = ax

        # Canvas
        self.canvas = FigureCanvas(self.fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()

        # Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)
        self.mplvl.addWidget(self.toolbar)

    def remove_figure_from_gui(self,):
        ''' Deletes the figure from the GUI. '''

        # Canvas
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.canvas.deleteLater()  # this prevents memory leaks

        # Toolbar
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()
        self.toolbar.deleteLater()  # this prevent memory leaks

    def save_parameters(self):
        parameters_dict = {
            'sw_min': str(self.startEdit.text()),
            'sw_max': str(self.endEdit.text()),
            'step': str(self.stepEdit.text()),
            'delay': int(self.delaySpinBox.value()),
            'decade': int(self.decadeComboBox.currentIndex()),
            'n': int(self.pocetMereniBox.value()),

            'log_sweep': self.logRadioButton.isChecked(),
            'lin_sweep': self.linRadioButton.isChecked(),
            'sense_local': self.senseLocalRadioButton.isChecked(),
            'sense_remote': self.senseRemoteRadioButton.isChecked(),

            'col_source': self.sourceCheckBox.checkState(),
            'col_delay': self.delayCheckBox.checkState(),
            'col_measure': self.measureCheckBox.checkState(),
            'col_time': self.timeCheckBox.checkState(),

            'stabilize_time': self.stableSpinBox.value(),
            'sleep_time': self.sleepSpinBox.value()
        }

        # For pickle, the file needs to be opened in binary mode, hence the "wb"
        with open("last_parameters.pickle", "wb") as params_file:
            pickle.dump(parameters_dict, params_file)

    def load_parameters(self):
        try:
            # For pickle, the file needs to be opened in binary mode, hence the "wb"
            with open("last_parameters.pickle", "rb") as params_file:
                parameters_dict = pickle.load(params_file)

            self.startEdit.setText(parameters_dict['sw_min'])
            self.endEdit.setText(parameters_dict['sw_max'])
            self.stepEdit.setText(parameters_dict['step'])
            self.delaySpinBox.setValue(parameters_dict['delay'])
            self.decadeComboBox.setCurrentIndex(parameters_dict['decade'])
            self.pocetMereniBox.setValue(parameters_dict['n'])

            self.logRadioButton.setChecked(parameters_dict['log_sweep'])
            self.linRadioButton.setChecked(parameters_dict['lin_sweep'])
            self.senseLocalRadioButton.setChecked(parameters_dict['sense_local'])
            self.senseRemoteRadioButton.setChecked(parameters_dict['sense_remote'])

            self.sourceCheckBox.setChecked(parameters_dict['col_source'])
            self.delayCheckBox.setChecked(parameters_dict['col_delay'])
            self.measureCheckBox.setChecked(parameters_dict['col_measure'])
            self.timeCheckBox.setChecked(parameters_dict['col_time'])

            self.stableSpinBox.setValue(parameters_dict['stabilize_time'])
            self.sleepSpinBox.setValue(parameters_dict['sleep_time'])

            self.switch_linear()

            print("Nacteni poslednich parametru uspesne! :)")

        except:
            print("Nacteni poslednich parametru selhalo. :(")

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
        self.sweep_id = '{0:%Y-%m-%d_%H-%M-%S}'.format(datetime.datetime.now())

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

        sense_local = self.senseLocalRadioButton.isChecked()
        sense_remote = self.senseRemoteRadioButton.isChecked()
        self.sense_local = sense_local

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
            self.save_parameters()
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

        # Local or Remote sense?
        if self.sense_local:
            print("Zapinam Sense - LOCAL.")
            self.inst.write("O0X")
        else:
            print("Zapinam Sense - REMOTE.")
            self.inst.write("O1X")

        # Úvodní stabilizace
        stabilize_time = self.stableSpinBox.value()
        print("Uvodni stabilizace v DC modu - {} s.".format(stabilize_time))
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

                print('Ukladam docasna data...')
                self.dump_data()

                n_hotovych_mereni += 1
                self.bigProgBar.setValue(n_hotovych_mereni)
                self.plot_data(data)

                if n_hotovych_mereni != n:
                    sleep_time = self.sleepSpinBox.value()
                    print("Pauza mezi sweepy - {} s.".format(sleep_time))
                    self.artSleep(sleep_time)

            else:
                print("Output byl prazdny. Prerusene mereni?")

        self.inst.operate(False)
        self.enable_ui(True)

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
        print('Jeden sweep hotov.')
        self.littleProgBar.setValue(100)

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
            self.senseLocalRadioButton,
            self.senseRemoteRadioButton,
            self.sourceCheckBox,
            self.delayCheckBox,
            self.measureCheckBox,
            self.timeCheckBox,
            self.stableSpinBox,
            self.sleepSpinBox,
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
            self.exportButton.setText('Export')

    def get_export_data(self):
        output = ""
        output += '# ======== Sweep ID: ' + self.sweep_id + ' ========' + '\n'
        output += '# ======== ' + str(len(self.full_data)) + ' sweeps' + ' ========' + '\n'

        output += self.get_measurement_parameters()

        for data in self.full_data:
            output += '# ======== SWEEP START ========\n'
            output += data.replace(',', '    ')
            output += '# ======== SWEEP END ========\n\n'

        return output

    def dump_data(self):
        save_file_name = 'C:\Repa\k237\data_temp.txt'
        try:
            with open(save_file_name, "w", encoding="utf-8") as text_file:
                text = self.get_export_data()
                text_file.write(text)
        except:
            print("Nouzovy dump se nepovedl.")

    def export_data(self):
        """
        Exportuje data pomocí ukládacího dialogu Qt. V případě chybného zadání
        souboru nic neudělá a postěžuje si do konzole.
        """
        proposed_name = self.sweep_id

        # Qt Dialog na výběr souboru k uložení
        save_file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            'Exportovat výsledky měření',
            'C:\Repa\k237\data\sweep_' + proposed_name + '.txt',
            'Text Files (*.txt);;All Files (*)'
        )

        # Vlastní uložení souboru
        try:
            with open(save_file_name, "w", encoding="utf-8") as text_file:
                text = self.get_export_data()
                text_file.write(text)

            # Update GUI
            self.exportButton.setText('Export ✔')
        except:
            print("Export neuspesny. Data pravdepodobne nejsou ulozena!")

            # Update GUI
            self.exportButton.setText('Export ✗')

    def get_measurement_parameters(self):
        out = ''
        out += "# Sweep ID: {}\n".format(self.sweep_id)
        if self.log_sweep:
            out += "# Log sweep:\n"
            out += "# Rozsah (min, max) [A]: {}, {}\n".format(self.startEdit.text(),
                                                              self.endEdit.text()
                                                              )
            out += "# Bodů na dekádu [-]: {}\n".format(self.decade_combo_values[self.decadeComboBox.currentIndex()])
        else:
            out += "# Linear sweep\n"
            out += "# Rozsah (min, max, points) [A]: {}, {}, {}\n".format(self.startEdit.text(),
                                                                          self.endEdit.text(),
                                                                          self.stepEdit.text()
                                                                          )

        out += "# Delay [ms]: {}\n".format(self.delaySpinBox.value())
        out += "# Počet charakteristik [-]: {}\n".format(self.pocetMereniBox.value())

        if self.sense_local:
            out += "# Sense: local\n"
        else:
            out += "# Sense: remote\n"

        out += "# Sloupce (Source, Measure, Delay, Time): {} {} {} {}\n".format(int(self.sourceCheckBox.checkState() / 2),
                                                                                int(self.measureCheckBox.checkState() / 2),
                                                                                int(self.delayCheckBox.checkState() / 2),
                                                                                int(self.timeCheckBox.checkState() / 2)
                                                                                )

        out += "# Uvodní DC stabilizace [s]: {}\n".format(self.stableSpinBox.value())
        out += "# Stabilizace [s]: {}\n".format(self.sleepSpinBox.value())

        return out
