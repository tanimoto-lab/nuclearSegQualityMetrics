This repository contains the code of a small python utility and an associated pyQt5
GUI for computing binary classification metrics (precision, recall, f-measure and accuracy)
for nuclear identification in 3D LSM stacks.

Compilation command using PyInstaller 3.3.1

`pyinstaller --hidden-import=PyQt5.sip --hidden-import=pandas._libs.tslibs.np_datetime --hidden-import=pandas._libs.tslibs.nattype --hidden-import=pandas._libs.skiplist --hidden-import=scipy._lib.messagestream --path D:\Windows\Installations\Anaconda3\envs\nuclearSegQualMetrics\Lib\site-packages\scipy\extra-dll segQualityMetricsQT.py`

IMPORTANT:
There could be trouble with compilation when pacakges are installed using conda. The last successful
build was with packages installed from pip. 