# -*- coding: utf-8 -*-
import sys
import os
import time
import datetime
import pickle
from PyQt5 import QtCore, QtGui, QtWidgets

from gui import Ui_sweepergui
from k237 import Instrument
import delays
import misc

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)


class GuiProgram(Ui_sweepergui):

    cols = 0
    sweep_id = 'mereni'
    full_data = []
    negative_current = False
    log_sweep = True
    stop = True
    decade_combo_values = ['5', '10', '25', '50']
    save_directory = False
    save_filename = False

    def __init__(self, dialog):
        Ui_sweepergui.__init__(self)
        self.setupUi(dialog)

        # Connect "add" button with a custom function (addInputTextToListbox)
        self.exportButton.clicked.connect(self.export_data)
        self.startBtn.clicked.connect(self.startFunc)
        self.logRadioButton.clicked.connect(self.switch_linear)
        self.linRadioButton.clicked.connect(self.switch_linear)
        self.dynamicDelayRadio.clicked.connect(self.switch_dynamic_delay)
        self.constantDelayRadio.clicked.connect(self.switch_dynamic_delay)

        # Populate comboBox
        self.decadeComboBox.clear()
        self.decadeComboBox.addItems(self.decade_combo_values)
        self.decadeComboBox.setCurrentIndex(1)

        self.exportButton.setEnabled(False)

        # Try to load last parameters from Pickle
        self.load_parameters()

        self.save_directory = os.path.dirname(os.path.abspath(__file__))

        # Připojení k instrumentu
        #self.inst = Instrument('GPIB0::17::INSTR', visa_location='C:\WINDOWS\SysWOW64\\visa32.dll')
        self.inst = Instrument('GPIB0::17::INSTR', virtual=False)

    # --- PLOTTING -----------------------------------------------------------
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

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

        self.canvas.get_default_filename = self.get_default_filename
        self.canvas.draw()  # Propagate changes to GUI

    def clear_plot(self):
        self.ax.clear()  # Clear contents of current axis
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

    def get_default_filename(self):
        """
        Return a string, which includes extension, suitable for use as
        a default filename.
        """
        default_basename = self.save_filename or "sweep_{}".format(self.sweep_id) or 'image'
        default_filetype = self.canvas.get_default_filetype()
        default_filename = default_basename + '.' + default_filetype

        save_dir = os.path.expanduser(matplotlib.rcParams.get('savefig.directory', ''))

        # ensure non-existing filename in save dir
        i = 1
        while os.path.isfile(os.path.join(save_dir, default_filename)):
                # attach numerical count to basename
            default_filename = '{0}_({1}).{2}'.format(default_basename, i, default_filetype)
            i += 1

        return default_filename

    # --- GUI collecting and starting MEASUREMENTS ---------------------------
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

    def validateInput(self, sw_min, sw_max, decade, delay, log_sweep, step):
        # Unit testing :P
        try:
            a = float(sw_min)
            a = float(sw_max)
            if not log_sweep:
                a = float(step)
        except:
            return False, "Některé parametry se nedají převést na čísla."

        # Code
        if log_sweep:
            if (float(sw_min) > 0 and
                float(sw_max) > 0 and
                    float(sw_min) != float(sw_max)):
                return True, "OK"
            else:
                return False, "Kraje intervalu jsou stejné nebo je alespoň jeden záporný."
        else:
            # lin sweep
            if (float(sw_min) != float(sw_max) and abs(float(sw_max) - float(sw_min)) > float(step)):
                # step fits into (start, stop) interval and start != stop
                test_array = np.arange(float(sw_max), float(sw_min), float(step))
                if self.chkLoop.checkState() and len(test_array) * 2 > 1000:
                    return False, "Počet bodů ve sweepu je {} > 1000. \nBuffer by přetekl, zvolte jemnější krok, menší rozsah nebo vypněte obousměrnost měření.".format(2 * len(test_array))
                elif len(test_array) > 1000:
                    return False, "Počet bodů ve sweepu je {} > 1000. \nBuffer by přetekl, zvolte jemnější krok nebo menší rozsah.".format(len(test_array))
                else:
                    return True, "OK"
            else:
                return False, "Kraje intervalu se rovnají, nebo je krok větší než rozsah."

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
        self.save_filename = False

        sense_local = self.senseLocalRadioButton.isChecked()
        sense_remote = self.senseRemoteRadioButton.isChecked()
        self.sense_local = sense_local

        sw_min = str(self.startEdit.text())
        sw_max = str(self.endEdit.text())
        step = str(self.stepEdit.text())

        # Pokud je zapojený zesilovač
        if not self.sense_local:
            sw_min = str(float(sw_min) * 1e3)
            sw_max = str(float(sw_max) * 1e3)
            step = str(float(step) * 1e3)

        # TODO: this should be made more logical...
        self.custom_capacity_used = self.dynamicDelayRadio.isChecked()
        if self.custom_capacity_used:
            self.custom_capacity = int(self.capacitySpinBox.value())

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

        input_valid, err = self.validateInput(sw_min, sw_max, decade, delay, log_sweep, step)
        if self.chkAutorange.checkState():
            sweep_range = '0'
        else:
            sweep_range = str(misc.get_range_number(float(sw_min), float(sw_max)))
            if sweep_range == '0':
                print('POZOR: Manualni nastaveni range selhalo, prilis vysoke proudy?')

        if input_valid:
            self.save_parameters()
            self.measure(sw_min, sw_max, decade, delay, log_sweep, step, n, sweep_range)
        else:
            self.show_notification(err)

    # --- ACTUAL MEASUREMENTS ------------------------------------------------
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

    def measure(self, sw_min, sw_max, decade, delay, log_sweep, step, n, sweep_range):
        ''' Spustí měření s již validovanými parametry. '''
        # Disable UI
        self.enable_ui(False)

        # Smaže aktuální graf
        self.clear_plot()

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
            self.inst.write("Q2," + sw_min + "," + sw_max + "," +
                            decade + "," + sweep_range + "," + delay + "X")
            if self.chkLoop.checkState():
                self.inst.write("Q8," + sw_max + "," + sw_min + "," +
                                decade + "," + sweep_range + "," + delay + "X")
        else:
            self.inst.write("Q1," + sw_min + "," + sw_max + "," +
                            step + "," + sweep_range + "," + delay + "X")
            if self.chkLoop.checkState():
                self.inst.write("Q7," + sw_max + "," + sw_min + "," +
                                step + "," + sweep_range + "," + delay + "X")

        # Manual modification of delays for each value
        if self.custom_capacity_used:
            if self.chkLoop.checkState():
                delay_arr = delays.delays_round(float(sw_min), float(
                    sw_max), int(decade), self.custom_capacity)
            else:
                delay_arr = delays.delays_up(float(sw_min), float(
                    sw_max), int(decade), self.custom_capacity)
            self.inst.set_custom_delays(delay_arr)

        data = []
        self.full_data = []
        self.np_data = []
        n_hotovych_mereni = 0
        for mereni in range(n):
            if self.stop:
                break
            output = self.run_sweep()
            if output:
                if not self.sense_local:
                    output = misc.shift_data(output, cols=self.cols, shift=-3)
                sweep_results = misc.nice_format(output, cols=self.cols)
                unpacked_results = misc.unpack(sweep_results, cols=self.cols)
                data.append(unpacked_results)
                self.full_data.append(sweep_results)
                self.np_data = misc.pack_data(self.np_data, unpacked_results)

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

    # --- EXPORT and DATA operations -----------------------------------------
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

    def dump_data(self):
        save_file_name = 'C:\Repa\k237\data_temp.txt'
        try:
            np.savetxt(save_file_name, self.np_data, fmt='%.4e',
                       header=self.get_measurement_parameters() + "\nPOZOR, prubezne ukladana data mohou byt nekompletni", delimiter='\t')
        except:
            print("Nouzovy dump se nepovedl.")

    def export_data(self):
        """
        Exportuje data pomocí ukládacího dialogu Qt. V případě chybného zadání
        souboru nic neudělá a postěžuje si do konzole.
        """

        proposed_name = self.save_filename or 'sweep_' + self.sweep_id

        # Qt Dialog na výběr souboru k uložení
        save_file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            'Exportovat výsledky měření',
            #'C:\Repa\k237\data\sweep_' + proposed_name + '.txt',
            os.path.join(self.save_directory, proposed_name + '.txt'),
            'Text Files (*.txt);;All Files (*)'
        )

        # Vlastní uložení souboru
        try:
            np.savetxt(save_file_name, self.np_data, fmt='%.4e',
                       header=self.get_measurement_parameters(), delimiter='\t')

            # Update GUI
            self.exportButton.setText('Export ✔')
            self.save_directory = os.path.dirname(save_file_name)
            self.save_filename = os.path.splitext(os.path.basename(save_file_name))[0]
        except:
            print("Export neuspesny. Data pravdepodobne nejsou ulozena!")

            # Update GUI
            self.exportButton.setText('Export ✗')

    def get_measurement_parameters(self):
        out = ''
        out += "Sweep ID: {}\n".format(self.sweep_id)
        if self.log_sweep:
            out += "Log sweep:\n"
            out += "Rozsah (min, max) [A]: {}, {}\n".format(self.startEdit.text(),
                                                            self.endEdit.text()
                                                            )
            out += "Bodu na dekadu [-]: {}\n".format(
                self.decade_combo_values[self.decadeComboBox.currentIndex()])
        else:
            out += "Linear sweep\n"
            out += "Rozsah (min, max, points) [A]: {}, {}, {}\n".format(self.startEdit.text(),
                                                                        self.endEdit.text(),
                                                                        self.stepEdit.text()
                                                                        )

        out += "Delay [ms]: {}\n".format(self.delaySpinBox.value())
        out += "Pocet charakteristik [-]: {}\n".format(self.pocetMereniBox.value())

        if self.sense_local:
            out += "Sense: local\n"
        else:
            out += "Sense: remote\n"

        out += "Sloupce (Source, Measure, Delay, Time): {} {} {} {}\n".format(int(self.sourceCheckBox.checkState() / 2),
                                                                              int(self.measureCheckBox.checkState(
                                                                              ) / 2),
                                                                              int(self.delayCheckBox.checkState(
                                                                              ) / 2),
                                                                              int(self.timeCheckBox.checkState(
                                                                              ) / 2)
                                                                              )

        out += "Uvodni DC stabilizace [s]: {}\n".format(self.stableSpinBox.value())
        out += "Stabilizace [s]: {}\n".format(self.sleepSpinBox.value())
        out += "\nI[A] (x)\tU[V .e-3] (y1, y2, ...) "

        return out

    # --- GUI parameters and ENABLE/DISABLE ----------------------------------
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

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
            'sleep_time': self.sleepSpinBox.value(),

            'chk_loop': self.chkLoop.checkState(),
            'chk_lock_range': self.chkLockRange.checkState(),
            'chk_autorange': self.chkAutorange.checkState(),
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

            self.chkLoop.setChecked(parameters_dict['chk_loop'])
            self.chkLockRange.setChecked(parameters_dict['chk_lock_range'])
            self.chkAutorange.setChecked(parameters_dict['chk_autorange'])

            self.switch_linear()
            self.switch_dynamic_delay()

            print("Nacteni poslednich parametru uspesne! :)")

        except:
            print("Nacteni poslednich parametru selhalo. :(")

    def switch_linear(self):
        log_sweep = self.logRadioButton.isChecked()
        lin_sweep = self.linRadioButton.isChecked()
        if log_sweep:
            self.stepEdit.setEnabled(False)
            self.decadeComboBox.setEnabled(True)
        else:
            self.decadeComboBox.setEnabled(False)
            self.stepEdit.setEnabled(True)

    def switch_dynamic_delay(self):
        const_delay = self.constantDelayRadio.isChecked()
        dynamic_delay = self.dynamicDelayRadio.isChecked()
        if const_delay:
            self.capacitySpinBox.setEnabled(False)
            self.delaySpinBox.setEnabled(True)
        else:
            self.delaySpinBox.setEnabled(False)
            self.capacitySpinBox.setEnabled(True)

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
            self.chkLoop,
            self.chkAutorange,
            self.exportButton,
        ]

        for element in ui_elements:
            element.setEnabled(status)

        if status:
            self.switch_linear()
            self.switch_dynamic_delay()

        if status:
            self.startBtn.clicked.disconnect()
            self.startBtn.clicked.connect(self.startFunc)
            self.startBtn.setText("Start")
            self.exportButton.setFocus()
        else:
            self.startBtn.clicked.disconnect()
            self.startBtn.clicked.connect(self.stopFunc)
            self.startBtn.setText("Abort")
            self.startBtn.setFocus()
            self.exportButton.setText('Export')

    def artSleep(self, sleepTime):
        """
        Čeká čas sleepTime v sekundách, zatím ale každých 50 milisekund řeší
        akce, o které se někdo pokoušel v GUI.
        """
        stop_time = QtCore.QTime()
        stop_time.restart()
        while stop_time.elapsed() < sleepTime * 1000:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 50)

    def show_notification(self, err):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Chybné parametry sweepu.")
        msg.setInformativeText(err)
        msg.setWindowTitle("Sweeper - varování")
        msg.exec_()
