# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from gui import Ui_sweepergui
from gui_obsluha import GuiProgram
from k237 import Instrument

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# TODO - poslední sweep by neměl sleepovat
# TODO - upravovat delaye pro každou dekádu zvlášť
# TODO - přepínání Sense - local/remote
# TODO - sundat omezení na políčka
# TODO - MODIFY log sweep - různý delay v různých oblastech
# TODO - hodně čudlíkovejch paramterů...
# TODO - export - přidat hlavičku datům podle sloupců
# TODO - export - vymyslet jak oddělovat jednotlive VA charakteristiky v jednom souboru
# TODO - interface - blokovat prvky co nemají být aktivní
# TODO - přesunout printy jen pod "debug" flag v Instrument objektu
# TODO - cleanup (vypnutí operate etc) při erroru programu
# TODO - Disable export if nothing measured
# DONE - Ošetřit cancel Export dialogu tak aby nespadnul program
# DONE - lineární sweep?
# DONE - probublávání errorů při běhu programu výš (abych je viděl)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()

    prog = GuiProgram(dialog)

    fig = Figure()  # empty figure to be put into GUI
    fig.set_tight_layout(True)
    ax1f1 = fig.add_subplot(111)  # empty plot
    prog.put_figure_into_gui(fig, ax1f1)
    prog.make_pretty()

    dialog.show()
    sys.exit(app.exec_())
