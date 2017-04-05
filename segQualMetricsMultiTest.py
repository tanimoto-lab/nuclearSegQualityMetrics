from SegmentationQualityMetrics import saveResultsTestList
import sys
import json

assert len(sys.argv) == 2, 'Invalid Usage. Please use as: ' \
                           '\'python segQualMetricsMultiTest.py <json paramater file>\''
pars = json.load(open(sys.argv[1]))
gtLabelImageFile = pars['gtLabelImageFile']
testLabelImageFiles = pars['testLabelImageFiles']
testLabels = pars['testImageFileLabels']
outputDir = pars['outputDir']
saveResultsTestList(testLabelImageFiles, gtLabelImageFile, outputDir, testLabels)
