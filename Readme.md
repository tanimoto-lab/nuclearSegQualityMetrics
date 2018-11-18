Description
----
This repository contains the code of a small python utility and an associated pyQt5
GUI for computing binary classification metrics (precision, recall, f-measure and accuracy)
for nuclear identification in 3D LSM stacks.

Installation
----
See install.md

Compilation
----
The application can be compiled into a standalone QT application using the following steps. Note: Only PyInstaller v3.3.1 was tested. The application may not compile successfully with other versions.

1. Activate the conda environment created in 'install.md'
2. Navigate into the directory containing segQualityMetricsQT.py
3. Execute the following:

`pyinstaller --hidden-import=PyQt5.sip --hidden-import=pandas._libs.tslibs.np_datetime --hidden-import=pandas._libs.tslibs.nattype --hidden-import=pandas._libs.skiplist --hidden-import=scipy._lib.messagestream --path D:\Windows\Installations\Anaconda3\envs\nuclearSegQualMetrics\Lib\site-packages\scipy\extra-dll segQualityMetricsQT.py`

Note: The path of the folder extra-dll above needs to be changed depending the anaconda environment created in 'install.md'

`pyinstaller --windowed --add-data dist\segQualMetricsMultiTest\;dist\segQualMetricsMultiTest segQualityMetricsQT.py`
 

IMPORTANT:
There could be trouble with compilation when packages are installed using conda. The last successful
build was with packages installed from pip.

Usage
-----
The application can be run using the executable "segQualityMetricsQT" in the folder dist/segQualityMetricsQT.

Alternatively, the application can also be started directly using the following steps:

1. Activate the conda environment created in 'install.md'
2. Navigate into the directory containing segQualityMetricsQT.py
3. Execute `python segQualityMetricsQT.py`







