
<img src="docs/ico.png" width="90" height="90" align="left" />

# CMOST: A Python Toolkit for LAMOST Astronomical Data
![Scrutinizer build (GitHub/Bitbucket)](https://img.shields.io/scrutinizer/build/g/YunyuG/Cmost)
![Static Badge](https://img.shields.io/pypi/pyversions/cmost)
[![PyPI Version](https://img.shields.io/pypi/v/cmost?color=blue)](https://pypi.org/project/cmost/)
![Codecov](https://img.shields.io/codecov/c/github/YunyuG/Cmost)
![GitHub License](https://img.shields.io/github/license/YunyuG/Cmost)



CMOST is a Python toolkit specifically designed for processing FITS files from LAMOST astronomical telescope observations. At its core, it's a secondary encapsulation of `astropy`, offering efficient and user-friendly data parsing and basic analysis capabilities.

### Key Features
- 🚀 Simple API interface `read_fits`, making FITS file handling as effortless as using `pandas` to read Excel files.
- 🔍 line index calculation algorithms.
- 📊 Basic spectral preprocessing methods.
- 🌐 FTP API for downloading official LAMOST FITS files with asynchronous support.

We do not guarantee that the calculation results are 100% correct. If you find any defects or issues, please contact us. We would greatly appreciate it.