import pytest

import cmost as cst


def test_lick_use_FitsData_or_wavelengthFLux():
    fits_data = cst.read_fits("tests/test_data/spec-55859-F5902_sp01-001_dr7.fits.gz")
    with pytest.raises(Exception):
        lick_indices = cst.lick.compute_LickLineIndices(
            fits_data, wavelength=fits_data.wavelength, flux=fits_data.flux
        )  # same time

        lick_indices = cst.lick.compute_LickLineIndices(wavelength=fits_data.wavelength)
    lick_indices = cst.lick.compute_LickLineIndices(fits_data)
    lick_indices = cst.lick.compute_LickLineIndices(
        wavelength=fits_data.wavelength, flux=fits_data.flux
    )
