import pytest
import cmost as cst

fits_data = cst.read_fits("tests/data/spec-55859-F5902_sp01-001_dr7.fits.gz")

PANDAS_INSTALLED = True
try:
    import pandas as pd  # type:ignore
except ImportError:
    PANDAS_INSTALLED = False


@pytest.mark.skipif(not PANDAS_INSTALLED, reason="need pandas")
def test_lick_depends_pandas():
    lick_indices = cst.lick.compute_LickLineIndices(fits_data)
    assert isinstance(lick_indices, pd.Series)  # type:ignore


@pytest.mark.skipif(PANDAS_INSTALLED, reason="don't need pandas")
def test_lick_depends_pandas():
    lick_indices = cst.lick.compute_LickLineIndices(fits_data)
    assert isinstance(lick_indices, dict)  # type:ignore


def test_lick_use_FitsData_or_wavelengthFLux():
    with pytest.raises(Exception):
        lick_indices = cst.lick.compute_LickLineIndices(
            fits_data, wavelength=fits_data.wavelength, flux=fits_data.flux
        )  # same time

        lick_indices = cst.lick.compute_LickLineIndices(wavelength=fits_data.wavelength)
    lick_indices = cst.lick.compute_LickLineIndices(fits_data)
    lick_indices = cst.lick.compute_LickLineIndices(
        wavelength=fits_data.wavelength, flux=fits_data.flux
    )
