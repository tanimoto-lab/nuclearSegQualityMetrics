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


def segQualMetrics(testLabelImageFile: str,
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
    testTPs = [testLabels[x] for x in testTPInds]

    nTruePostive = len(testTPs)

    nGT = len(gtLabels)

    nTest = len(testLabels)

    nFalsePositive = nTest - nTruePostive

    nFalseNegative = nGT - nTruePostive

    recall = nTruePostive / nGT

    precision = nTruePostive / nTest

    fMeasure = 2 * (recall * precision) / (recall + precision)

    accuracy = nTruePostive / (nTruePostive + nFalseNegative + nFalsePositive)

    cellCount = nTest

    return cellCount, recall, precision, fMeasure, accuracy

def saveResultsTestList(testLabelImageFiles: typing.Iterable[str],
                        groundTruthLabelImagFile: str, outputDir: str,
                        labels) -> pd.DataFrame:
    assert len(labels) == len(testLabelImageFiles), 'Number of elements in labels ' \
                                                        'and testLabelImageFiles are not equal'

    nTest = len(testLabelImageFiles)
    resDF = pd.DataFrame()

    for label, testLabelImageFile in zip(labels, testLabelImageFiles):

        cellCount, recall, precision, fMeasure, accuracy = \
            segQualMetrics(testLabelImageFile, groundTruthLabelImagFile)
        tempDict = {'Recall': recall, 'Precision': precision, 'fMeasure': fMeasure, 'Accuracy': accuracy,
                    'testLabelImageFile': testLabelImageFile,
                    'groundTruthLabelImageFile': groundTruthLabelImagFile,
                    'label': label, 'cellCount': cellCount}
        resDF = resDF.append(tempDict, ignore_index=True)

    fig, ax = plt.subplots(figsize=(14, 11.2))

    tempDF = resDF.set_index(keys=['label'])
    tempDF = tempDF.sort_index()
    tempDF.plot(ax=ax, xticks=range(nTest),
                marker='o', ms=10, lw=3, )

    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

    ax.set_xlim(-0.5, nTest - 0.5)
    fig.tight_layout()
    fig.canvas.draw()
    fig.savefig(os.path.join(outputDir, 'metrics.png'), dpi=150)

    tempDF.to_excel(os.path.join(outputDir, 'metrics.xlsx'))

    plt.close(fig.number)
    del fig
    return resDF

if __name__ == '__main__':

    assert len(sys.argv) == 3, \
        "Invalid Usage. Correct usage: \'python <testLabelImageFile> <groundTruthImageFile>\'"

    testLabelImageFile = sys.argv[1]
    gTLabelImageFile = sys.argv[2]

    recall, precision, fMeasure, accuracy = segQualMetrics(testLabelImageFile=testLabelImageFile,
                                                           groundTruthLabeImageFile=gTLabelImageFile)
    print('Recall={}\nPrecision={}\nfMeasure={}\nAccuracy={}'.format(recall, precision, fMeasure, accuracy))




