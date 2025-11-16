# Copyright(C) YunyuG 2025. All rights reserved.
# Created at Sat Nov 15 21:14:23 CST 2025.

import cmost as cst
import pytest

PANDAS_INSTALLED = True
try:
    import pandas as pd  # type:ignore
except ImportError:
    PANDAS_INSTALLED = False

@pytest.fixture(scope="session")
def test_fits_data():
    fits_data = cst.read_fits("tests/data/spec-55859-F5902_sp01-001_dr7.fits.gz")
    return fits_data

@pytest.mark.skipif(not PANDAS_INSTALLED, reason="need pandas")
def test_lick_depends_pandas(test_fits_data):
    lick_indices = cst.lick.compute_LickLineIndices(test_fits_data)
    assert isinstance(lick_indices, pd.Series)  # type:ignore


@pytest.mark.skipif(PANDAS_INSTALLED, reason="don't need pandas")
def test_lick_not_depends_pandas(test_fits_data):
    lick_indices = cst.lick.compute_LickLineIndices(test_fits_data)
    assert isinstance(lick_indices, dict)


def test_lick_use_FitsData_or_wavelengthFLux(test_fits_data):
    fits_data = test_fits_data
    with pytest.raises(Exception):
        lick_indices = cst.lick.compute_LickLineIndices(
            fits_data, wavelength=fits_data.wavelength, flux=fits_data.flux
        )  # same time

        lick_indices = cst.lick.compute_LickLineIndices(wavelength=fits_data.wavelength)
    lick_indices = cst.lick.compute_LickLineIndices(fits_data) #noqa
    lick_indices2 = cst.lick.compute_LickLineIndices( # noqa
        wavelength=fits_data.wavelength, flux=fits_data.flux
    )

def test_lick_useless_LickIndicesTable(test_fits_data):
    useless_LickIndicesTable_path = "tests/data/index2.table"
    with pytest.raises(ValueError):
        lick_indices = cst.lick.compute_LickLineIndices(test_fits_data
                                                        ,LickLineIndex_table_path=useless_LickIndicesTable_path)
