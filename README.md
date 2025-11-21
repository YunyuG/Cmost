
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
- 🌐 FTP API for downloading official LAMOST FITS files with the support of multithreading.


# Install
You can use `pip` to install Cmost.
```bash
pip3 install cmost
```

# Read the fits file
The goal of `Cmost` is to simplify the process of reading FITS files. You can achieve this with minimal code, as shown below:
```python
import cmost as cst
import numpy as np

fits_data = cst.read_fits("path/to/fits")

wavelength = fits_data['Wavelength']
flux = fits_data['Flux']

# You can visit the info of header directly like this.

redshift = fits_data['z']
```

# Download
In fact,`pylamost` has already implemented this method,and we just copy it to our lib and created a functional interface of the multithreading to reduce the time spent on downloading.
```python
import cmost as cst
import numpy as np

obsids:list = ['100**',...] 

fits_downloader = cst.FitsDownloader("dr10","v2.0",TOKEN="*****")

for o in obsids:
    fits_downloader.download_fits(o)

# Using MultThread
fits_downloader.download_fits_use_MultiThreading(obsids)

```

# LickIndices
LickIndices is one of the important features to be used in machine learning.We also implement it.
```python
lick_indices = cst.lick.compute_LickLineIndices(test_fits_data)

print(lick_indices) # It is a pd.Series if pandas is installed, otherwise it is a dict.
 ```

We do not guarantee that the calculation results are 100% correct. If you find any defects or issues, please contact us. We would greatly appreciate it.
