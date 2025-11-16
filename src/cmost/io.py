# Copyright(C) YunyuG 2025. All rights reserved.
# Created at Sat Nov 15 21:14:23 CST 2025.

__all__ = ["read_fits"]

import re
import numpy as np

from astropy.io import fits
from .processing import (
    minmax_function,
    align_wavelength,
    remove_redshift,
    median_filter,
)


class FitsData:
    def __init__(self, wavelength: np.ndarray, flux: np.ndarray, header: dict):
        self.wavelength = wavelength
        self.flux = flux
        self.header = header

    def __getitem__(self, key):
        if key == "Wavelength":
            return self.wavelength
        elif key == "Flux":
            return self.flux
        else:
            return self.header[key]

    def minmax(self, range_: tuple = (0, 1)) -> "FitsData":
        new_flux = minmax_function(self.flux, range_)
        return FitsData(self.wavelength, new_flux, self.header)

    def align(self, aligned_wavelength: np.ndarray) -> "FitsData":
        new_flux = align_wavelength(self.wavelength, self.flux, aligned_wavelength)
        new_wavelength = aligned_wavelength
        return FitsData(new_wavelength, new_flux, self.header)

    def remove_redshift(self) -> "FitsData":
        Z = self.header["z"]
        new_flux = remove_redshift(self.wavelength, self.flux, Z)
        return FitsData(self.wavelength, new_flux, self.header)

    def median_filter(self, size: int = 7) -> "FitsData":
        new_flux = median_filter(self.flux, size)
        return FitsData(self.wavelength, new_flux, self.header)

    def visualize(self, ax=None):
        if ax:
            plot_spectrum(self.wavelength, self.flux, ax, is_show=False)
        else:
            plot_spectrum(self.wavelength, self.flux, is_show=True)

    @classmethod
    def from_hdu(cls, hdu):
        header: dict = dict()

        for key, value in zip(hdu[0].header.keys(), hdu[0].header.values()):
            if "COMMENT" in key or len(key) < 1:
                continue
            header[key.lower()] = value

        match = re.search(r"DR(\d{1,2})", header["data_v"])
        dr_version = int(match.group(1))

        data = hdu[0].data if dr_version < 8 else hdu[1].data[0]

        if dr_version < 8:
            # This part refers to the `read_lrs_fits` function in the `LAMOST` class of the `pylamost`` library
            # Specifically, see:
            #   https://github.com/fandongwei/pylamost
            coeff0 = header["coeff0"]
            coeff1 = header["coeff1"]
            pixel_num = header["naxis1"]
            wavelength = 10 ** (coeff0 + np.arange(pixel_num) * coeff1)
        else:
            wavelength = np.asarray(data[2], dtype=float)

        flux = np.asarray(data[0], dtype=float)
        andmask = np.asarray(data[3], dtype=int)
        orimask = np.asarray(data[4], dtype=int)

        if np.sum(orimask) > 0 or np.sum(andmask) > 0:
            header["exists_bad_points"] = 1
        else:
            header["exists_bad_points"] = 0

        return cls(wavelength, flux, header)

    def __repr__(self):
        return f"FitsData<filename={self.header['filename']}>"


def plot_spectrum(
    wavelength: np.ndarray, flux: np.ndarray, ax=None, is_show: bool = False
):
    try:
        import matplotlib.pyplot as plt  # lazy import
    except ImportError as e:
        raise ImportError(
            "You should install 'matplotlib' to use this method\n"
            "pip3 install matplotlib\n"
        ) from e
    rc_s = {
        "font.family": "Arial",
        "font.size": 14,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
        "mathtext.fontset": "cm",
    }

    plt.rcParams.update(rc_s)
    if ax:
        ax.plot(wavelength, flux)
    else:
        plt.plot(wavelength, flux)

    if is_show:
        plt.xlabel(r"Wavelength($\AA$)")
        plt.ylabel("Flux")
        plt.show()


def read_fits(fits_path: str) -> FitsData:
    with fits.open(fits_path) as hdu:
        return FitsData.from_hdu(hdu)
