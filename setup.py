from setuptools import setup, find_packages
setup(
        name="nuclearSegQualityMetrics",
        use_scm_version=True,
        setup_requires=['setuptools_scm'],
        packages=find_packages(exclude=["^\."]),
        exclude_package_data={'': ["Readme.txt"]},
        install_requires=["numpy>=1.11.2",
                          "matplotlib>=1.5.3",
                          "scipy>=0.18.1",
                          "pandas>=0.19.0",
                          "seaborn>=0.7.1",
                          "SimpleITK>=1.0.0",
                          "PyInstaller>=3.2.1",
                          "openpyxl>=2.4.1",
                          "PyQt5>=5.6.0",
                          "pillow>=3.4.2"],
        python_requires=">=3.6",
    )