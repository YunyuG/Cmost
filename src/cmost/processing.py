# Copyright(C) YunyuG 2025. All rights reserved.
# Created at Sat Nov 15 21:14:23 CST 2025.

import numpy as np
from scipy import interpolate, signal


def minmax_function(flux, range_: tuple) -> np.ndarray:
    flux = range_[0] + (range_[1] - range_[0]) * (flux - np.min(flux)) / (
        np.max(flux) - np.min(flux)
    )
    return flux


def align_wavelength(
    wavelength: np.ndarray,
    flux: np.ndarray,
    aligned_wavelength: np.ndarray,
    **kwargs,
) -> np.ndarray:
    kind = kwargs.get("kind", "linear")
    F = interpolate.interp1d(
        wavelength, flux, kind=kind, bounds_error=False, fill_value=(flux[0], flux[-1])
    )

    return F(aligned_wavelength)


def remove_redshift(
    wavelength_obs: np.ndarray, flux_rest: np.ndarray, Z: float, **kwargs
) -> np.ndarray:
    kind = kwargs.get("kind", "linear")
    wavelength_rest = wavelength_obs / (1 + Z)
    F = interpolate.interp1d(
        wavelength_rest,
        flux_rest,
        kind=kind,
        bounds_error=False,
        fill_value=(flux_rest[0], flux_rest[-1]),
    )
    return F(wavelength_obs)


def median_filter(flux: np.ndarray, size: int) -> np.ndarray:
    return signal.medfilt(flux, size)
