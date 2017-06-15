import nuclearSegQualityMetrics
import pathlib

baseLibPath = pathlib.Path(nuclearSegQualityMetrics.__path__[0]).parent
testFilesPath = baseLibPath / "tests" / "files"