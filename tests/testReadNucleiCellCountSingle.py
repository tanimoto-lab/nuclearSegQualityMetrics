from nuclearSegQualityMetrics.farsight_bindings import readNucleiSegCountSingle
from nuclearSegQualityMetrics.folderDefs import testFilesPath


testDir = testFilesPath / "CountingResults" / "test1_8bit"

cellCount = readNucleiSegCountSingle(str(testDir))

print(cellCount)
