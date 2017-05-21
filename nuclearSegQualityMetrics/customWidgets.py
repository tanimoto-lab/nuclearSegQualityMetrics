from PyQt5.QtWidgets import QGroupBox, QLabel, QSizePolicy, QPushButton, \
    QHBoxLayout, QFileDialog, QMessageBox
import os

def raiseInfo(str, parent):
    QMessageBox.information(parent, 'Warning!', str)


class pathSelect(QGroupBox):

    def getDir(self):

        pass

    def __init__(self, title, parent=None):

        QGroupBox.__init__(self, title, parent)

        self.dirPathW = QLabel()
        self.dirPathW.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.chooseDirPathB = QPushButton('Select')
        self.chooseDirPathB.setMaximumHeight(30)
        self.chooseDirPathB.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.chooseDirPathB.clicked.connect(self.getDir)

        hbox = QHBoxLayout()
        hbox.addWidget(self.dirPathW)
        hbox.addWidget(self.chooseDirPathB)

        self.dirPathW.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setMaximumHeight(60)

        self.setLayout(hbox)

    def setText(self, str):

        if os.path.isdir(str) or os.path.isfile(str) or str is '':
            self.dirPathW.setText(str)
        else:
            raiseInfo('No such file or directory: ' + str, self)
            # pass

    def getText(self):

        return self.dirPathW.text()

class DirSelect(pathSelect):

    def getDir(self):

        dirPath = QFileDialog.getExistingDirectory(parent=self,
                                                   directory=self.dialogDefaultPath,
                                                   caption=self.dialogTitle,
                                                   options=QFileDialog.ShowDirsOnly
                                                   )
        self.setText(dirPath)


    def __init__(self, title, parent=None, dialogTitle='',
                 dialogDefaultPath=None):

        super().__init__(title, parent)

        self.dialogTitle = dialogTitle
        if dialogDefaultPath is None or not os.path.isdir(dialogDefaultPath):
            dialogDefaultPath = os.path.expanduser('~')
        self.dialogDefaultPath = dialogDefaultPath


class FileSelect(pathSelect):


    def getDir(self):

        filePath, filter = QFileDialog.getOpenFileName(self, self.dialogTitle,
                                               self.dialogDefaultPath,
                                               self.dialogFileTypeFilter)
        self.setText(filePath)

    def __init__(self, title, parent=None,
                 dialogTitle='', dialogDefaultPath=None, dialogFileTypeFilter='All Files(*.*)'):

        super().__init__(title, parent)
        self.dialogTitle = dialogTitle
        if dialogDefaultPath is None or not os.path.isdir(dialogDefaultPath):
            dialogDefaultPath = os.path.expanduser('~')
        self.dialogDefaultPath = dialogDefaultPath
        self.dialogFileTypeFilter = dialogFileTypeFilter

