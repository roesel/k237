import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from sensor import Sensor
from datetime import datetime

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    s1_freq = 5  # [s]

    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtWidgets.QMenu(parent)

        submenu = QtWidgets.QMenu(menu)
        submenu.setTitle("Sensor 1")
        s1_5s = submenu.addAction("Every 5 s")
        s1_10s = submenu.addAction("Every 10 s")
        menu.addMenu(submenu)

        exitAction = menu.addAction("Exit")
        self.setContextMenu(menu)

        s1_5s.triggered.connect(lambda period=5: self.set_period(period))
        s1_10s.triggered.connect(lambda period=10: self.set_period(period))
        exitAction.triggered.connect(self.exit)

        print("Tray icon set up.")

        self.s1 = Sensor("COM8")

        self.run()

    def run(self):
        with open("C:\\Users\\roese\\Desktop\\temp_log.txt", 'a') as outfile:
            outfile.write("# Time                          Temp       Dewpoint   Humidity\n")
        while True:
            print("Sleeping for {} seconds.".format(self.s1_freq))
            self.artSleep(self.s1_freq * 1000)
            reading = self.s1.read()
            print(reading)
            with open("C:\\Users\\roese\\Desktop\\temp_log.txt", 'a') as outfile:
                outfile.write("{0:}      {1:.2f}      {2:.2f}      {3:.2f}\n".format(str(datetime.now()), reading["temperature"], reading["dewpoint"], reading["humidity"]))
            
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
    app = QtWidgets.QApplication(sys.argv)

    w = QtWidgets.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon("Logger.png"), w)

    trayIcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
