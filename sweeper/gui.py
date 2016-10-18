# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_sweepergui(object):
    def setupUi(self, sweepergui):
        sweepergui.setObjectName("sweepergui")
        sweepergui.resize(726, 511)
        self.gridLayout = QtWidgets.QGridLayout(sweepergui)
        self.gridLayout.setObjectName("gridLayout")
        self.mplwindow = QtWidgets.QWidget(sweepergui)
        self.mplwindow.setObjectName("mplwindow")
        self.mplvl = QtWidgets.QVBoxLayout(self.mplwindow)
        self.mplvl.setContentsMargins(0, 0, 0, 0)
        self.mplvl.setObjectName("mplvl")
        self.gridLayout.addWidget(self.mplwindow, 0, 0, 2, 1)
        self.outTextEdit = QtWidgets.QPlainTextEdit(sweepergui)
        self.outTextEdit.setObjectName("outTextEdit")
        self.gridLayout.addWidget(self.outTextEdit, 0, 1, 1, 1)
        self.startBtn = QtWidgets.QPushButton(sweepergui)
        self.startBtn.setObjectName("startBtn")
        self.gridLayout.addWidget(self.startBtn, 3, 1, 1, 1)
        self.pocetMereniBox = QtWidgets.QSpinBox(sweepergui)
        self.pocetMereniBox.setMinimum(1)
        self.pocetMereniBox.setMaximum(20)
        self.pocetMereniBox.setObjectName("pocetMereniBox")
        self.gridLayout.addWidget(self.pocetMereniBox, 2, 1, 1, 1)

        self.retranslateUi(sweepergui)
        QtCore.QMetaObject.connectSlotsByName(sweepergui)

    def retranslateUi(self, sweepergui):
        _translate = QtCore.QCoreApplication.translate
        sweepergui.setWindowTitle(_translate("sweepergui", "Sweeper"))
        self.startBtn.setText(_translate("sweepergui", "Start"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    sweepergui = QtWidgets.QDialog()
    ui = Ui_sweepergui()
    ui.setupUi(sweepergui)
    sweepergui.show()
    sys.exit(app.exec_())

