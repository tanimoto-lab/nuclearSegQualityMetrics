import os
import sys
from math import pi as PI

import SimpleITK as sitk
import numpy as np
import pandas as pd
import seaborn as sns
import typing
from matplotlib import pyplot as plt
from scipy.spatial import cKDTree

from nuclearSegQualityMetrics.matplotlibRCParams import mplPars

sns.set(rc=mplPars, style='darkgrid')


def getSphereRadius(volume: float) -> float:

    assert volume > 0, 'The Value of volume given is not positive'

    temp = 3 * volume / (4 * PI)

    return temp ** (1/3.0)


def labelCentroidRadius(labelImage: sitk.Image) -> tuple:

    labelStats = sitk.LabelShapeStatisticsImageFilter()
    labelStats.Execute(labelImage)

    labels = labelStats.GetLabels()

    centroids = [labelStats.GetCentroid(x) for x in labels]
    radii = [labelStats.GetEquivalentSphericalRadius(x) for x in labels]

    return labels, centroids, radii


def getMetricsFromCounts(nFP: float, nTP: float, nFN: float) -> typing.List[float]:

    recall = nTP / (nTP + nFN)

    precision = nTP / (nTP + nFP)

    fMeasure = 2 * (recall * precision) / (recall + precision)

    accuracy = nTP / (nTP + nFN + nFP)

    return recall, precision, fMeasure, accuracy


def segQualErrors(testLabelImageFile: str,
                  groundTruthLabeImageFile: str, saveDebugInfoTo: typing.Union[None, str] = None) -> tuple:

    testLabelImage = sitk.ReadImage(testLabelImageFile)
    gtLabelImage = sitk.ReadImage(groundTruthLabeImageFile)

    testShape = testLabelImage.GetSize()
    gtShape = gtLabelImage.GetSize()

    assert len(testShape) == 3, 'testLabelImage is not 3D'
    assert len(gtShape) == 3, 'groundTruthLabelImage is not 3D'

    assert testShape == gtShape, 'testLabelImage {} and groundTruthLabelImage {} ' \
                                 'do not have the same shape'.format(testLabelImageFile, groundTruthLabeImageFile)

    testLabels, testCentroids, testRadii = labelCentroidRadius(testLabelImage)
    gtLabels, gtCentroids, gtRadii = labelCentroidRadius(gtLabelImage)

    testCentroidKDTree = cKDTree(testCentroids, leafsize=100)
    nnDists, nnInds = testCentroidKDTree.query(gtCentroids)

    # mask for nnInds
    truePositiveMask = np.less_equal(nnDists, gtRadii)
    testTPInds = nnInds[truePositiveMask]
    testTPInds = list(set(testTPInds))
    testTPLabels = [testLabels[x] for x in testTPInds]

    testFPLabels = [x for x in testLabels if x not in testTPLabels]
    testFPCentroids = [y for x, y in zip(testLabels, testCentroids) if x not in testTPLabels]

    if len(testFPLabels):

        gtCentroidKDTree = cKDTree(gtCentroids, leafsize=100)
        # looking for nearest neighbours for among gtCentroids for each testFP
        gtNNDists, gtNNInds = gtCentroidKDTree.query(testFPCentroids)
        # looking for those FPs whose centroids are not in any gt sphere
        # In the sentence below, x in an index along testFPLabels, gtNNInds[x] is the index of the correspoding
        # NN among gtLabels
        noiseFPIndsAmongTestFPs = [x for x, y in enumerate(gtNNDists) if y > gtRadii[gtNNInds[x]]]
        noiseFPLabels = [testFPLabels[x] for x in noiseFPIndsAmongTestFPs]

        nonNoiseFPLabels = [x for x in testFPLabels if x not in noiseFPLabels]

    else:
        noiseFPLabels = []
        nonNoiseFPLabels = []

    gtClassification = ["TP" if x else "FN" for x in truePositiveMask]
    testClassification = []

    for testLabel in testLabels:

        if testLabel in testTPLabels:
            testClassification.append("TP")
        elif testLabel in noiseFPLabels:
            testClassification.append("FP-Noise")
        else:
            testClassification.append("FP-NonNoise")

    testLabelImageStub = os.path.split(testLabelImageFile)[1].split(".")[0]
    gTLabelImageFileStub = os.path.split(groundTruthLabeImageFile)[1].split(".")[0]

    outdirStub = "{}_{}".format(testLabelImageStub, gTLabelImageFileStub)
    localOutputDir = os.path.join(saveDebugInfoTo, outdirStub)

    if not os.path.isdir(localOutputDir):
        os.mkdir(localOutputDir)

    if saveDebugInfoTo:
        writeDebugInfoTo(gtCentroids, gtLabels, gtRadii,
                         gtClassification,
                         os.path.join(localOutputDir, "gtData.xlsx"))
        writeDebugInfoTo(testCentroids, testLabels, testRadii,
                         testClassification,
                         os.path.join(localOutputDir, "testData.xlsx"))

    nTP = len(testTPLabels)

    nGT = len(gtLabels)

    nTest = len(testLabels)

    nFP = nTest - nTP

    nFN = nGT - nTP

    nNoiseFP = len(noiseFPLabels)
    nNonNoiseFP = len(nonNoiseFPLabels)

    assert nNoiseFP + nNonNoiseFP == nFP, "NoiseFPs and NonNoiseFPs don't union up to FalsePositives"

    return nFP, nTP, nFN, nNoiseFP, nNonNoiseFP

def writeDebugInfoTo(centroids, labels, radii, classification, outputFile):

    df = pd.DataFrame(index=labels)
    df["Centroids"] = list(map(str, map(lambda x: np.around(x, 2), centroids)))
    df["Classification"] = classification
    df["Radii"] = radii

    df.to_excel(outputFile)


def saveResultsTestList(testLabelImageFiles: typing.Iterable[str],
                        groundTruthLabelImagFile: str, outputDir: str,
                        labels: typing.Iterable[str], saveDebugInfo: bool = False) -> pd.DataFrame:
    assert len(labels) == len(testLabelImageFiles), 'Number of elements in labels ' \
                                                        'and testLabelImageFiles are not equal'

    nTest = len(testLabelImageFiles)
    resDF = pd.DataFrame()

    if saveDebugInfo:
        saveDebugInfoTo = outputDir
    else:
        saveDebugInfoTo = None
    for label, testLabelImageFile in zip(labels, testLabelImageFiles):
        nFP, nTP, nFN, nNoiseFP, nNonNoiseFP= \
            segQualErrors(testLabelImageFile, groundTruthLabelImagFile, saveDebugInfoTo=saveDebugInfoTo)
        recall, precision, fMeasure, accuracy = getMetricsFromCounts(nFP, nTP, nFN)
        testCellCount = nFP + nTP
        gtCellCount = nTP + nFN
        tempDict = {'Recall': recall, 'Precision': precision, 'fMeasure': fMeasure, 'Accuracy': accuracy,
                    'testLabelImageFile': testLabelImageFile,
                    'groundTruthLabelImageFile': groundTruthLabelImagFile,
                    'label': label, 'testCellCount': testCellCount, 'groundTruthCellCount': gtCellCount,
                    'nFP': nFP, 'nTP': nTP, 'nFN': nFN, 'nNoiseFP': nNoiseFP, 'nNonNoiseFP': nNonNoiseFP}
        resDF = resDF.append(tempDict, ignore_index=True)

    fig0, ax0 = plt.subplots(figsize=(14, 11.2))

    tempDF = resDF.set_index(keys=['label'])
    tempDF = tempDF.sort_index()
    tempDF.plot(ax=ax0, xticks=range(nTest), y=['Recall', 'Precision', 'fMeasure', 'Accuracy'],
                marker='o', ms=10, lw=3, )

    ax0.set_xticklabels(ax0.get_xticklabels(), rotation=90)

    ax0.set_xlim(-0.5, nTest - 0.5)
    fig0.tight_layout()
    fig0.canvas.draw()
    fig0.savefig(os.path.join(outputDir, 'metrics.png'), dpi=150)

    fig1, ax1 = plt.subplots(figsize=(14, 11.2))
    tempDF.plot(ax=ax1, xticks=range(nTest), y=['testCellCount'], marker='o', ms=10, lw=3, color='b')
    ax1.plot(ax1.get_xlim(), [gtCellCount, gtCellCount], 'r:', lw=3, label='ground Truth')
    ax1.legend(loc='best')
    ax1.set_xlim(-0.5, nTest - 0.5)
    ax1.set_xticklabels(ax0.get_xticklabels(), rotation=90)
    fig1.tight_layout()
    fig1.canvas.draw()
    fig1.savefig(os.path.join(outputDir, 'cellCounts.png'), dpi=150)

    tempDF.to_excel(os.path.join(outputDir, 'metrics.xlsx'))

    for fig in [fig0, fig1]:
        plt.close(fig.number)
        del fig
    return resDF

if __name__ == '__main__':

    assert len(sys.argv) == 3, \
        "Invalid Usage. Correct usage: \'python <testLabelImageFile> <groundTruthImageFile>\'"

    testLabelImageFile = sys.argv[1]
    gTLabelImageFile = sys.argv[2]

    nFP, nTP, nFN, nNoiseFP, nNonNoiseFP = segQualErrors(testLabelImageFile=testLabelImageFile,
                                                         groundTruthLabeImageFile=gTLabelImageFile)
    nTest = nFP + nTP
    nGT = nTP + nFN

    recall, precision, fMeasure, accuracy = getMetricsFromCounts(nFP, nTP, nFN)
    print('nFP={}\nnTP={}\nnFN={}\nnNoiseFP={}\nnNonNoiseFP={}'.format(nFP, nTP, nFN, nNoiseFP, nNonNoiseFP))
    print('Recall={}\nPrecision={}\nfMeasure={}\nAccuracy={}'.format(recall, precision, fMeasure, accuracy))




