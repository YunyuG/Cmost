# Copyright(C) YunyuG 2025. All rights reserved.
# Created at Sat Nov 15 21:14:23 CST 2025.

import cmost as cst
import pytest
import numpy as np

MATPLOTLIB_INSTALLED = True
try:
    import matplotlib.pyplot as plt
except ImportError:
    MATPLOTLIB_INSTALLED = False

@pytest.fixture(scope="session")
def test_fits_data():
    fits_data = cst.read_fits("tests/data/spec-55859-F5902_sp01-001_dr7.fits.gz")
    return fits_data


def test_read_on_different_dr_version():
    fits_data = cst.read_fits("tests/data/spec-55859-F5902_sp01-001_dr7.fits.gz") #noqa
    fits_data2 = cst.read_fits("tests/data/spec-55859-F5902_sp01-013_dr8.fits.gz") #noqa
    print(fits_data2)

def test_minmax(test_fits_data):
    fits_data = test_fits_data
    fits_data2 = fits_data.minmax()
    assert max(fits_data2.flux)==1
    assert min(fits_data2.flux)==0

def test_remove_redshift(test_fits_data):
    fits_data = test_fits_data
    fits_data2 = fits_data.remove_redshift() #noqa

def test_align(test_fits_data):
    fits_data = test_fits_data
    aligned_wavelength = np.arange(3700,9100,2)
    fits_data2 = fits_data.align(aligned_wavelength) #noqa
    assert len(fits_data2['Flux']) == len(aligned_wavelength)
    assert len(fits_data2['Wavelength']) == len(aligned_wavelength)

def test_median_filter(test_fits_data):
    fits_data = test_fits_data
    fits_data2 = fits_data.median_filter() # noqa

@pytest.mark.skipif(not MATPLOTLIB_INSTALLED,reason="need matplotlib")
def test_visualize(test_fits_data):
    ax = plt.gca()
    test_fits_data.visualize(ax)

