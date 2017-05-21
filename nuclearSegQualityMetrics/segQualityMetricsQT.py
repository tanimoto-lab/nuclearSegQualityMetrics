import inspect
import json
import os
import platform
import sys

from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, \
    QMessageBox, QDesktopWidget, QTableWidget, QTextEdit, \
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QCheckBox, QGroupBox, QLineEdit

from nuclearSegQualityMetrics.customWidgets import FileSelect, DirSelect, raiseInfo


def getShortenedPath(path, showLast=2, compressWith='.....'):

    parts = path.split(os.sep)

    if len(parts) <= showLast + 1:

        return path
    else:
        toRetain = [parts[0], compressWith] + parts[-showLast:]
        return os.path.join(*toRetain)


def getAllFilesInTree(dir, filter=None):

    files = []
    for dirName, subDirList, fileList in os.walk(dir):

        dirFull = os.path.abspath(dirName)
        if filter is not None:
            fileList = [x for x in fileList if x.endswith(filter)]
        files += [os.path.join(dirFull, file) for file in fileList]
    return files

class CentralWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.initui()
        self.initSegQualPy()

    def initui(self):
        self.gtLabelImageSelect = FileSelect(title='Ground Truth Label Image',
                                        parent=self,
                                        dialogDefaultPath=None,
                                        dialogFileTypeFilter='Label Image(*.tif)',
                                        dialogTitle='Choose Ground Truth Label Image'
                                        )
        self.testFolder = DirSelect(title='Folder containing test images',
                               parent=self,
                               dialogTitle='Choose folder containing test images',
                               dialogDefaultPath=None)

        mainVBox = QVBoxLayout()
        mainVBox.addWidget(self.gtLabelImageSelect)
        mainVBox.addWidget(self.testFolder)

        tableActionButtons = QHBoxLayout()
        mainVBox.addLayout(tableActionButtons)

        refreshButton = QPushButton('Load Tiff Files in TestFolder')
        refreshButton.clicked.connect(self.loadTiffs)

        self.tiffFiles = []

        tableActionButtons.addWidget(refreshButton)

        self.tiffTable = QTableWidget(self)
        self.loadTable()
        mainVBox.addWidget(self.tiffTable)

        self.opDirSelect = DirSelect(title='Output Folder',
                               parent=self,
                               dialogTitle='Choose folder OutputFolder',
                               dialogDefaultPath=None)
        mainVBox.addWidget(self.opDirSelect)

        runGroupBox = QGroupBox(self)
        runBox = QHBoxLayout(self)

        runControlBox = QVBoxLayout(self)
        startButton = QPushButton('Run')
        startButton.clicked.connect(self.runSegQualMetrics)

        self.interruptButton = QPushButton('Interrupt')

        runControlBox.addWidget(startButton)
        runControlBox.addWidget(self.interruptButton)

        self.outputDisplay = QTextEdit()
        self.outputDisplay.setReadOnly(True)

        runBox.addWidget(self.outputDisplay)
        runBox.addLayout(runControlBox)
        runGroupBox.setLayout(runBox)

        mainVBox.addWidget(runGroupBox)

        self.setLayout(mainVBox)

    def initSegQualPy(self):

        oneDirUp = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.segQualPy = os.path.join(oneDirUp, 'dist', 'segQualMetricsMultiTest',
                                      'segQualMetricsMultiTest.exe')

    def getcheckedTiffList(self):

        checkedTiffFiles = []
        checkedTiffFileLabels = []
        for rowInd in range(self.tiffTable.rowCount()):
            item = self.tiffTable.cellWidget(rowInd, 0)
            label = self.tiffTable.cellWidget(rowInd, 1).text()
            if item.isChecked():
                checkedTiffFiles.append(self.tiffFiles[rowInd])
                checkedTiffFileLabels.append(label)
        return checkedTiffFiles, checkedTiffFileLabels

    def writeJSONParams(self, gtLabelImage, testImages, testFileLabels, outDir):

        pars = {}
        pars['gtLabelImageFile'] = gtLabelImage
        pars['testLabelImageFiles'] = testImages
        pars['testImageFileLabels'] = testFileLabels
        pars['outputDir'] = outDir
        jsonFile = os.path.join(self.parent().appDataHome, 'temp.json')
        json.dump(pars, open(jsonFile, 'w'))
        return jsonFile

    def runSegQualMetrics(self):

        checkedTiffFiles, checkedTiffFileLabels = self.getcheckedTiffList()
        gtLabelImage = self.gtLabelImageSelect.getText()
        outputDir = self.opDirSelect.getText()
        currentData = 'ground Truth Image File:\n{}\n\ntest images:\n{}.\n' \
                       .format(gtLabelImage, '\n'.join(checkedTiffFiles))
        checkMessage = currentData + 'Are you sure you want to proceed?'
        reply = QMessageBox.question(self, 'Check Parameters', checkMessage,
                                     QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)

        if reply == QMessageBox.Yes:
            jsonFile = self.writeJSONParams(gtLabelImage, checkedTiffFiles, checkedTiffFileLabels, outputDir)
            proc = QProcess(self)
            self.interruptButton.clicked.connect(proc.kill)
            self.outputDisplay.append('Calculating metrics for:\n{}\nPlease Wait. The program may take '
                                      'a few minutes to finish......'.format(currentData))
            proc.start(self.segQualPy, [jsonFile])
            proc.finished.connect(self.checkoutput)
            proc.errorOccurred.connect(self.printTerminated)

    def printTerminated(self):

        self.sender().terminate()
        self.outputDisplay.append('Calculation Terminated. No Output generated.')

    def checkoutput(self, exitCode, exitStatus):

        sender = self.sender()
        print(exitCode)
        print(exitStatus)
        if exitStatus == QProcess.NormalExit:
            if exitCode != 0:
                raiseInfo('Error:\n{}'.format(sender.readAllStandardError()), self)
            else:
                self.outputDisplay.append('Finished Succesfully. '
                                          'Metrics written into {}'.format(self.opDirSelect.getText()))
        else:
            raiseInfo('Error:\n{}'.format(sender.readAllStandardError()), self)
    def loadTiffs(self):

        testFolder = self.testFolder.getText()

        if not os.path.isdir(testFolder):
            raiseInfo('Invalid Test Folder: {}'.format(testFolder), self)
        else:
            self.tiffFiles = getAllFilesInTree(testFolder, '.tif')

        self.loadTable()


    def loadTable(self):

        self.tiffTable.setRowCount(len(self.tiffFiles))
        self.tiffTable.setColumnCount(2)
        self.tiffTable.setHorizontalHeaderLabels(['Tiff File', 'Label'])

        for ind, tifffile in enumerate(self.tiffFiles):

            shortenedTiffFilePath = getShortenedPath(tifffile)
            checkBox = QCheckBox(shortenedTiffFilePath, self)
            checkBox.setChecked(1)
            self.tiffTable.setCellWidget(ind, 0, checkBox)

            label = QLineEdit(self)
            label.setText('File{}'.format(ind + 1))
            self.tiffTable.setCellWidget(ind, 1, label)

        self.tiffTable.resizeColumnsToContents()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):


        exitAction = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        self.initAppHome()

        centralWidget = CentralWidget(self)
        self.setCentralWidget(centralWidget)


        self.setWindowTitle('Tanimoto Lab Nuclei Segmentation Pipeline')
        self.setGeometry(300, 300, 500, 700)
        self.center()
        # self.setWindowIcon(QIcon('web.png'))
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
        if not os.path.isdir(self.appDataHome):
            os.mkdir(self.appDataHome)

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