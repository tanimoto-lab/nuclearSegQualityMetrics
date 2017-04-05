# from farsight_bindings import readNucleiSegCountDir, plotCellCounts
# opDir = 'C:/Users/Ajayrama/Documents/Takahiro/countingResults'
# cellCounts = readNucleiSegCountDir(opDir)
# print(cellCounts)
# plotCellCounts(opDir)

from SegmentationQualityMetrics import saveResultsTestList

gtLabelImageFile = \
    'C:/Users/Ajayrama/Documents/Takahiro/countingResults/' \
    'test1_8bit_CLAHE3D64053/test1_8bit_CLAHE3D64053.tif'

testLabelImageFiles = [
    'C:/Users/Ajayrama/Documents/Takahiro/countingResults/test1_8bit/test1_8bit.tif',
    'C:/Users/Ajayrama/Documents/Takahiro/countingResults/test1_8bit_CLAHE3D64053/test1_8bit_CLAHE3D64053.tif',
    'C:/Users/Ajayrama/Documents/Takahiro/countingResults/test1_8bit_median1_CLAHE3D64053/'
    'test1_8bit_median1_CLAHE3D64053.tif',
    'C:/Users/Ajayrama/Documents/Takahiro/countingResults/test1_8bit_CLAHE3D64053_median1/'
    'test1_8bit_CLAHE3D64053_median1.tif'
]

labels = ['nothing', 'just CLAHE', 'median then CLAHE', 'CLAHE then median']
opDir = 'C:/Users/Ajayrama/Documents/Takahiro/plotsEtc/test1'

saveResultsTestList(testLabelImageFiles, gtLabelImageFile, opDir, labels)