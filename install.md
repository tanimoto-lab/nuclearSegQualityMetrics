Using the package requires the anaconda python distribution (https://www.anaconda.com/download)

Here are the steps:

1. Create a new environment with conda environment

`conda create -n cellCounting python=3.5 numpy pandas matplotlib scipy pillow seaborn pyqt=5`

2. Activate the environment

`conda activate cellCounting`

3. Install SimpleITK

`conda install -c https://conda.anaconda.org/simpleitk SimpleITK`

4. Navigate into the downloaded repository

`cd \path\to\the\folder\nuclearSegQualityMetrics`

5. Install the package

`pip install nuclearSegQualityMetrics`