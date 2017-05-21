# from farsight_bindings import readNucleiSegCountDir, plotCellCounts
# opDir = 'C:/Users/Ajayrama/Documents/Takahiro/countingResults'
# cellCounts = readNucleiSegCountDir(opDir)
# print(cellCounts)
# plotCellCounts(opDir)

import os

from nuclearSegQualityMetrics.SegmentationQualityMetrics import saveResultsTestList

homeFolder = 'C:/Users/Ajayrama/Documents/Takahiro'

gtLabelImageFile = os.path.join(homeFolder, 'metricsTest', 'verysmall.labels(255).tif')


testLabelImageFiles = [
    os.path.join(homeFolder, 'metricsTest', 'verysmall_test.tif')
]

labels = ['test']
opDir = 'C:/Users/Ajayrama/Documents/Takahiro/plotsEtc/metricsTest'

saveResultsTestList(testLabelImageFiles, gtLabelImageFile, opDir, labels, saveDebugInfo=True)