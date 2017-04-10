import numpy as np
import SimpleITK as sitk
from math import pi as PI
from scipy.spatial import cKDTree
import typing
import sys
import pandas as pd
from matplotlib import pyplot as plt
import os
from matplotlibRCParams import mplPars
import seaborn as sns
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
                  groundTruthLabeImageFile: str) -> tuple:

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
        # looking those FPs whose centroids are not in any gt sphere
        noiseFPIndsAmongTestFPs = [x for x, y in enumerate(gtNNDists) if y > gtRadii[x]]
        noiseFPLabels = [testFPLabels[x] for x in noiseFPIndsAmongTestFPs]

        nonNoiseFPLabels = [x for x in testFPLabels if x not in noiseFPLabels]

    else:
        noiseFPLabels = []
        nonNoiseFPLabels = []

    nTP = len(testTPLabels)

    nGT = len(gtLabels)

    nTest = len(testLabels)

    nFP = nTest - nTP

    nFN = nGT - nTP

    nNoiseFP = len(noiseFPLabels)
    nNonNoiseFP = len(nonNoiseFPLabels)

    assert nNoiseFP + nNonNoiseFP == nFP, "NoiseFPs and NonNoiseFPs don't union up to FalsePositives"

    return nFP, nTP, nFN, nNoiseFP, nNonNoiseFP


def saveResultsTestList(testLabelImageFiles: typing.Iterable[str],
                        groundTruthLabelImagFile: str, outputDir: str,
                        labels) -> pd.DataFrame:
    assert len(labels) == len(testLabelImageFiles), 'Number of elements in labels ' \
                                                        'and testLabelImageFiles are not equal'

    nTest = len(testLabelImageFiles)
    resDF = pd.DataFrame()

    for label, testLabelImageFile in zip(labels, testLabelImageFiles):
        nFP, nTP, nFN, nNoiseFP, nNonNoiseFP= \
            segQualErrors(testLabelImageFile, groundTruthLabelImagFile)
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




