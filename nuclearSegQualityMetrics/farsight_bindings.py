import os
import shutil
import subprocess
import sys

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from tifffile import imread

from nuclearSegQualityMetrics.matplotlibRCParams import mplPars

sns.set(rc=mplPars, style='darkgrid')


def runNucleiSegSingle(inputImageFile, outputDir, farSightBinDir, paramFile=None, verify_replace=True):

    assert os.path.isfile(inputImageFile), 'Input image {} not found'.format(inputImageFile)
    assert os.path.isdir(farSightBinDir), 'Farsight Bin directory {} not found'.format(farSightBinDir)
    assert os.path.isdir(outputDir), 'Output Directory {} not found'.format(outputDir)

    if paramFile is not None:
        assert os.path.isfile(paramFile), 'Param File {} not found'.format(paramFile)

    ipFilePath, ipFileName = os.path.split(inputImageFile)
    ipFileNamePrefix, ipFileNameSuffix = ipFileName.split('.')
    imgOPDir = os.path.join(outputDir, ipFileNamePrefix)

    if os.path.exists(imgOPDir):
        if verify_replace:
            ch = input('Image Output Directory {} already exists. Replace?(y/n)'.format(imgOPDir))

            if ch == 'y':
                shutil.rmtree(imgOPDir)
            else:
                sys.exit(1)
        else:
            shutil.rmtree(imgOPDir)

    os.mkdir(imgOPDir)

    segment_nucleiBin = os.path.join(farSightBinDir, 'segment_nuclei.exe')

    assert os.path.isfile(segment_nucleiBin), 'segment_nuclei.exe not found in ' \
                                              'Farsight bin directory at {}'.format(farSightBinDir)

    opFile = os.path.join(imgOPDir, ipFileName)
    logFileName = os.path.join(imgOPDir, '{}Log.log'.format(ipFileNamePrefix))

    toCall = [segment_nucleiBin, inputImageFile, opFile]

    if paramFile:
        toCall += paramFile

    with open(logFileName, 'w') as logFile:
        try:
            if paramFile:
                print('Started: segment_nuclei on {} with parameters from {}......'.format(inputImageFile, paramFile))
            else:
                print('Started: segment_nuclei on {} with default parameters......'.format(inputImageFile))

            subprocess.run(toCall, timeout=600, check=True, stdout=logFile, stderr=logFile)
        except subprocess.CalledProcessError as e:
            raise(RuntimeError('segment_nuclei failed on {} with parameter file {}'.format(inputImageFile, paramFile)))

    segFinalDatWrong = os.path.join(ipFilePath, '{}_seg_final.dat'.format(ipFileNamePrefix))
    segFinalDatCorrect = os.path.join(imgOPDir, '{}_seg_final.dat'.format(ipFileNamePrefix))

    shutil.move(segFinalDatWrong, segFinalDatCorrect)

    seedPointsWrong = os.path.join(ipFilePath, '{}_seedPoints.txt'.format(ipFileNamePrefix))
    seedPointsRight = os.path.join(imgOPDir, '{}_seedPoints.txt'.format(ipFileNamePrefix))

    shutil.move(seedPointsWrong, seedPointsRight)

    if paramFile:
        print('Finished: segment_nuclei on {} with parameters from {}.'.format(inputImageFile, paramFile))
    else:
        print('Finished: segment_nuclei on {} with default parameters.'.format(inputImageFile))


def runNucleiSegFolder(dir, outputDir, farSightBinDir, fileSuffix = '.tif', paramFile=None, verify_replace=True):

    assert os.path.isdir(dir), 'Input Directory {} not found'.format(dir)
    assert os.path.isdir(farSightBinDir), 'Farsight Bin directory {} not found'.format(farSightBinDir)
    assert os.path.isdir(outputDir), 'Output Directory {} not found'.format(outputDir)

    if paramFile is not None:
        assert os.path.isfile(paramFile), 'Param File {} not found'.format(paramFile)

    inputFileNames = [x for x in os.listdir(dir) if x.endswith(fileSuffix)]

    if not inputFileNames:
        raise(FileNotFoundError('No files with suffix {} found in {}'.format(fileSuffix, dir)))

    existantImgOPDirs = []
    for ipFN in inputFileNames:
        ipP, ipS = ipFN.split('.')
        imgOutputDir = os.path.join(outputDir, ipP)
        if os.path.isdir(imgOutputDir):
            existantImgOPDirs.append(imgOutputDir)

    if not existantImgOPDirs:
        if verify_replace:

            ch = input('The following results already exist\n{}\nReplace them?(y/n):'.format(existantImgOPDirs))
            if ch == 'y':
                [shutil.rmtree(x) for x in existantImgOPDirs]
            else:
                sys.exit(1)

        else:
            [shutil.rmtree(x) for x in existantImgOPDirs]

    for ipFN in inputFileNames:
        ipP, ipS = ipFN.split('.')
        inImageFile = os.path.join(dir, ipFN)
        runNucleiSegSingle(inputImageFile=inImageFile,
                           outputDir=outputDir,
                           farSightBinDir=farSightBinDir,
                           paramFile=paramFile,
                           verify_replace=False)


def readNucleiSegCountSingle(imgOutputDir):

    assert os.path.isdir(imgOutputDir), 'Output Directory {} not found'.format(imgOutputDir)

    imgPrefix = os.path.split(imgOutputDir)[1]

    labelImg = os.path.join(imgOutputDir, imgPrefix + '.tif')

    assert os.path.isfile(labelImg), 'Label image {} not found'.format(labelImg)

    img = imread(labelImg)

    cellCount = img.max() + 1

    return cellCount

def readNucleiSegCountDir(outputDir):

    assert os.path.isdir(outputDir), 'Output Directory {} not found'.format(outputDir)

    cellCounts = {}
    for imgOPDirName in os.listdir(outputDir):

        imgOPDir = os.path.join(outputDir, imgOPDirName)
        if os.path.isdir(imgOPDir):
            imgFullPath = os.path.join(imgOPDir, imgOPDirName + '.tif')
            if os.path.isfile(imgFullPath):
                cellCount = readNucleiSegCountSingle(imgOPDir)
                cellCounts[imgOPDirName] = cellCount

    return cellCounts

def plotCellCounts(outputDir):

    assert os.path.isdir(outputDir), 'Output Directory {} not found'.format(outputDir)

    cellCounts = readNucleiSegCountDir(outputDir)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.bar(np.arange(len(cellCounts)), cellCounts.values())
    ax.set_xticks(np.arange(len(cellCounts)))
    ax.set_xticklabels(cellCounts.keys(), rotation=90)
    fig.tight_layout()
    fig.canvas.draw()
    plt.show()

