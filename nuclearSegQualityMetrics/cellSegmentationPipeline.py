import os
import platform
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QMessageBox, \
    QAction, QWidget, QVBoxLayout, QHBoxLayout

from nuclearSegQualityMetrics.customWidgets import FileSelect


def raiseInfo(str, parent):
    QMessageBox.information(parent, 'Warning!', str)

class SettingsWindow(QWidget):

    def __init__(self, icyExecutable, imagejExecutable, farsightExecutable):

        super().__init__()
        self.initui(icyExecutable, imagejExecutable, farsightExecutable)

    def initui(self, icyExecutable, imagejExecutable, farsightExecutable):
        self.setWindowTitle('Settings')
        self.setGeometry(300, 300, 250, 150)

        self.imageJBinSelect = FileSelect(title='ImageJ Executable',
                                     dialogTitle='Select ImageJ Executable',
                                     dialogFileTypeFilter='Executable(*.exe)',
                                     dialogDefaultPath=imagejExecutable)
        self.farsightBinSeclect = FileSelect(title='Farsight Executable',
                                        dialogTitle='Select Farsight Executable',
                                        dialogFileTypeFilter='Executable(*.exe)',
                                        dialogDefaultPath=farsightExecutable)
        self.icyBinSelect = FileSelect(title='Icy Excecutable',
                                  dialogTitle='Select Icy Executable',
                                  dialogFileTypeFilter='Executable(*.exe)',
                                  dialogDefaultPath=icyExecutable)

        vbox = QVBoxLayout()
        vbox.addWidget(self.imageJBinSelect)
        vbox.addWidget(self.farsightBinSeclect)
        vbox.addWidget(self.icyBinSelect)

        applyCancelBox = QHBoxLayout()
        applyAction = QAction(QIcon('apply.png'), 'Apply', self)
        applyAction.setStatusTip('Apply the new setting and close')
        applyAction.triggered.connect(self.apply)

        self.show()

    def apply(self):
        return self.icyBinSelect.getText(), \
               self.farsightBinSeclect.getText(), \
               self.imageJBinSelect.getText()

    def cancel(self):
        return None


class ExectableSettings(object):

    def __init__(self):

        super().__init__()
        self.farsightExecutable = None
        self.icyExecutable = None
        self.imagejExecutable = None

    def changeSettings(self):

        settingsWindow = SettingsWindow(icyExecutable=self.icyExecutable,
                                        farsightExecutable=self.farsightExecutable,
                                        imagejExecutable=self.imagejExecutable)




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.center()
        self.setWindowTitle('Tanimoto Lab Nuclei Segmentation Pipeline')
        self.setGeometry(500, 500, 250, 150)
        # self.setWindowIcon(QIcon('web.png'))

        exitAction = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        settingsAction = QAction(QIcon('settings.png'), 'Settings', self)
        settingsAction.setStatusTip('Change Settings')
        settingsAction.triggered.connect(changeSettings)
        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        toolbar = self.addToolBar('Tools')
        toolbar.addAction(exitAction)
        self.initAppHome()


        self.show()



    def initAppHome(self):

        system = platform.system()
        userHome = os.path.expanduser('~')

        if system == 'Windows':
            self.appDataHome = os.path.join(userHome, 'AppData', 'Local', 'TanimotoLabCellSeg')
        elif system == 'Linux':
            self.appDataHome = os.path.join(userHome, '.TanimotoLabCellSeg')
        else:
            raiseInfo('We are sorry, but we do not support your operating system {}.'
                      'We currently support only Windows and Linux.'.format(system), self)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):

        # TODO check if any processes are running. Include this in message
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())