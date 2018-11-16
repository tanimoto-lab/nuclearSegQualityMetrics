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
The application can be compiled into a standalone QT application using the following commands with the folder containing "segQualityMetricsQT.py". Note: Only PyInstaller v3.3.1 was tested. The application may not compile successfully with othe versions.

`pyinstaller.exe segQualMetricsMultiTest.py`

`pyinstaller --windowed --add-data dist\segQualMetricsMultiTest\;dist\segQualMetricsMultiTest segQualityMetricsQT.py`
 

Usage
-----
The application can be run using the executable "segQualityMetricsQT" in the folder dist/segQualityMetricsQT.

Alternatively, the application can also be started directly using the following steps:

1. Activate the conda environment created in 'install.md'
2. Navigate into the directory containing segQualityMetricsQT.py
3. Execute `python segQualityMetricsQT.py`