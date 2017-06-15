import inspect
import os
import platform
import sys

from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, \
    QMessageBox, QDesktopWidget, QTableWidget, QTextEdit, \
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QCheckBox, QGroupBox, QLineEdit

from nuclearSegQualityMetrics.customWidgets import FileSelect, DirSelect, raiseInfo
from nuclearSegQualityMetrics.SegmentationQualityMetrics import saveResultsTestList

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

class SegQualityMetricsThread(QThread):

    def __init__(self, testLabelImageFiles: list,
                 gtLabelImageFile: str, testLabels: list, outputDir: str):
        self.testLabelImageFiles = testLabelImageFiles
        self.gtLabelImageFile = gtLabelImageFile
        self.testLabels = testLabels
        self.outputDir = outputDir
        self.terminated = False

        super().__init__()

    def run(self):
        saveResultsTestList(testLabelImageFiles=self.testLabelImageFiles,
                            groundTruthLabelImagFile=self.gtLabelImageFile,
                            outputDir=self.outputDir,
                            labels=self.testLabels,
                            saveDebugInfo=True)


class CentralWidget(QWidget):
    startCalcSig = pyqtSignal(list, str, list, str)

    def __init__(self, parent):
        super().__init__(parent)
        self.initui()
        self.calcThread = SegQualityMetricsThread(None, None, None, None)


    def initui(self):

        mainVBox = QVBoxLayout()

        self.gtLabelImageSelect = FileSelect(title='Ground Truth Label Image',
                                        dialogDefaultPath=None,
                                        dialogFileTypeFilter='Label Image(*.tif)',
                                        dialogTitle='Choose Ground Truth Label Image'
                                        )
        self.testFolder = DirSelect(title='Folder containing test images',
                               dialogTitle='Choose folder containing test images',
                               dialogDefaultPath=None)


        mainVBox.addWidget(self.gtLabelImageSelect)
        mainVBox.addWidget(self.testFolder)

        tableActionButtons = QHBoxLayout()
        mainVBox.addLayout(tableActionButtons)

        refreshButton = QPushButton('Load Tiff Files in TestFolder')
        refreshButton.clicked.connect(self.loadTiffs)

        self.tiffFiles = []

        tableActionButtons.addWidget(refreshButton)

        self.tiffTable = QTableWidget()
        self.loadTable()
        mainVBox.addWidget(self.tiffTable)

        self.opDirSelect = DirSelect(title='Output Folder',
                               parent=self,
                               dialogTitle='Choose folder OutputFolder',
                               dialogDefaultPath=None)
        mainVBox.addWidget(self.opDirSelect)

        runGroupBox = QGroupBox(self)
        runBox = QHBoxLayout()

        runControlBox = QVBoxLayout()
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

            self.calcThread.__init__(checkedTiffFiles,
                                   gtLabelImage,
                                   checkedTiffFileLabels,
                                   outputDir)
            self.calcThread.start()
            self.outputDisplay.append('Calculating metrics for:\n{}\nPlease Wait. The program may take '
                                     'a few minutes to finish......'.format(currentData))
            self.interruptButton.clicked.connect(self.termicateCalc)
            self.calcThread.finished.connect(self.handleSQMFinished)

    def termicateCalc(self):
        self.calcThread.terminated = True
        self.calcThread.terminate()


    def handleSQMFinished(self):

        if self.calcThread.terminated:
            self.outputDisplay.append('Calculation Terminated. No Output generated.')
        else:
            self.outputDisplay.append('Finished Succesfully. '
                                          'Metrics written into {}'.format(self.opDirSelect.getText()))

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


        self.setWindowTitle('Segmentation Quality Metrics')
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