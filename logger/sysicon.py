import sys
from PyQt4 import QtGui, QtCore


class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtGui.QMenu(parent)

        submenu = QtGui.QMenu(menu)
        submenu.setTitle("Sensor 1")
        s1_5s = submenu.addAction("Every 5 s")
        s1_10s = submenu.addAction("Every 10 s")
        menu.addMenu(submenu)

        exitAction = menu.addAction("Exit")
        self.setContextMenu(menu)
        QtCore.QObject.connect(exitAction, QtCore.SIGNAL('triggered()'), self.exit)

        QtCore.QObject.connect(s1_5s, QtCore.SIGNAL('triggered()'),
                               lambda period=5: self.set_period(period))
        QtCore.QObject.connect(s1_10s, QtCore.SIGNAL('triggered()'),
                               lambda period=10: self.set_period(period))

        print("Tray icon set up.")

    def artSleep(self, sleepTime):
        stop_time = QtCore.QTime()
        stop_time.restart()
        while stop_time.elapsed() < sleepTime:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 50)

    def set_period(self, period):
        print("Measuring period set to {}.".format(period))

    def exit(self):
        QtCore.QCoreApplication.exit()


def main():
    app = QtGui.QApplication(sys.argv)

    w = QtGui.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon("Logger.png"), w)

    trayIcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
