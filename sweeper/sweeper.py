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

# DONE - probublávání errorů při běhu programu výš (abych je viděl)
# TODO - hodně čudlíkovejch paramterů...
# TODO - export - přidat hlavičku datům podle sloupců
# TODO - export - vymyslet jak oddělovat jednotlive VA charakteristiky v jednom souboru
# TODO - interface - blokovat prvky co nemají být aktivní
# DONE - lineární sweep?
# TODO - přesunout printy jen pod "debug" flag v Instrument objektu
# TODO - cleanup (vypnutí operate etc) při erroru programu
# TODO - Export - multiple sweeps in multiple columns etc?
# TODO - Disable export if nothing measured

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()

    prog = GuiProgram(dialog)

    # Prázdný plot pro GUI
    fig1 = Figure()
    ax1f1 = fig1.add_subplot(111)
    prog.addmpl(fig1)

    dialog.show()
    sys.exit(app.exec_())
