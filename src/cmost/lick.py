# Copyright(C) YunyuG 2025. All rights reserved.
# Created at Sat Nov 15 21:14:23 CST 2025.

import os
import csv
import numpy as np
from functools import cache
from collections import namedtuple
from scipy import interpolate, integrate
from .io import FitsData

__all__ = ["compute_LickLineIndices"]

PANDAS_INSTALLED: bool = True
try:
    import pandas as pd  # type:ignore
except ImportError:
    PANDAS_INSTALLED = False

LickLineIndex = namedtuple(
    "LickLineIndex",
    [
        "index_band_start",
        "index_band_end",
        "blue_continuum_start",
        "blue_continuum_end",
        "red_continuum_start",
        "red_continuum_end",
        "units",
        "index_name",
    ],
)


@cache
def _read_LickLineIndex(fp: str) -> list[LickLineIndex]:
    col_names: list = [
        "num",
        "index_band_start",
        "index_band_end",
        "blue_continuum_start",
        "blue_continuum_end",
        "red_continuum_start",
        "red_continuum_end",
        "units",
        "index_name",
    ]
    res: list = []
    with open(fp, "r", encoding="utf-8") as file:
        next(file)
        csv_file = csv.DictReader(file, col_names, delimiter=" ")
        v_error = ValueError(
                "The lick line index table does not meet the program's expectations."
                "You need to ensure that the table format is as follows:\n\n"
                "##   Index band       blue continuum   red continuum  Units name\n"
                "01 4142.125 4177.125 4080.125 4117.625 4244.125 4284.125 1 CN_1\n"
                "02 4142.125 4177.125 4083.875 4096.375 4244.125 4284.125 1 CN_2\n"
                "03 4222.250 4234.750 4211.000 4219.750 4241.000 4251.000 0 Ca4227\n"
                "04 4281.375 4316.375 4266.375 4282.625 4318.875 4335.125 0 G4300\n"
            ) 
        try:
            for row in csv_file:
                row_item: LickLineIndex = LickLineIndex(
                    float(row["index_band_start"]),
                    float(row["index_band_end"]),
                    float(row["blue_continuum_start"]),
                    float(row["blue_continuum_end"]),
                    float(row["red_continuum_start"]),
                    float(row["red_continuum_end"]),
                    int(row["units"]),
                    row["index_name"],
                )
                res.append(row_item)
        except Exception as e:
            raise v_error from e
    if len(res)==0:
        raise v_error
    return res


def compute_LickLineIndices(
    fits_data: FitsData = None,
    *,
    wavelength: np.ndarray = None,
    flux: np.ndarray = None,
    LickLineIndex_table_path: str | None = None,
) -> dict | pd.Series:  # type:ignore
    if not ((wavelength is not None and flux is not None) ^ (fits_data is not None)):
        raise ValueError("must provide either `wavelength` and `flux` or `fits_data`")

    if LickLineIndex_table_path is None:
        LickLineIndex_table_path = os.path.join(
            os.path.join(os.path.abspath(os.path.join(__file__, os.pardir)), "assets"),
            "index.table",
        )

    LickLineIndex_table = _read_LickLineIndex(LickLineIndex_table_path)

    if fits_data is not None:
        wavelength = np.asarray(fits_data.wavelength)
        flux = np.asarray(fits_data.flux)
    else:
        wavelength = np.asarray(wavelength)
        flux = np.asarray(flux)

    if not PANDAS_INSTALLED:
        res = dict()
    else:
        res = pd.Series()

    for lick_line_index in LickLineIndex_table:
        (wavelength_FI_lambda, flux_FI_lambda, wavelength_FC_lambda, flux_FC_lambda) = (
            compute_FI_lambda_FC_lambda(wavelength, flux, lick_line_index)
        )
        if lick_line_index.units == 0:
            res[lick_line_index.index_name] = compute_EW(
                wavelength_FI_lambda,
                flux_FI_lambda,
                wavelength_FC_lambda,
                flux_FC_lambda,
            )
        else:
            res[lick_line_index.index_name] = compute_Mag(
                wavelength_FI_lambda,
                flux_FI_lambda,
                wavelength_FC_lambda,
                flux_FC_lambda,
            )
    return res


def compute_FI_lambda_FC_lambda(
    wavelength: np.ndarray, flux: np.ndarray, lick_line_index: LickLineIndex
) -> tuple[np.ndarray]:
    func = interpolate.interp1d(wavelength, flux, kind="linear")

    wavelength_FI_lambda, flux_FI_lambda = extract_one_spectrum(
        wavelength,
        flux,
        lick_line_index.index_band_start,
        lick_line_index.index_band_end,
        func=func,
    )

    wavelength_blue_continuum, flux_blue_continuum = extract_one_spectrum(
        wavelength,
        flux,
        lick_line_index.blue_continuum_start,
        lick_line_index.blue_continuum_end,
        func=func,
    )

    wavelength_red_continuum, flux_red_continuum = extract_one_spectrum(
        wavelength,
        flux,
        lick_line_index.red_continuum_start,
        lick_line_index.red_continuum_end,
        func=func,
    )

    blue_wavelength_mid = (
        lick_line_index.blue_continuum_start + lick_line_index.blue_continuum_end
    ) / 2
    red_wavelength_mid = (
        lick_line_index.red_continuum_start + lick_line_index.red_continuum_end
    ) / 2

    blue_mean_flux = compute_mean_flux(wavelength_blue_continuum, flux_blue_continuum)
    red_mean_flux = compute_mean_flux(wavelength_red_continuum, flux_red_continuum)

    F = interpolate.interp1d(
        y=[blue_mean_flux, red_mean_flux],
        x=[blue_wavelength_mid, red_wavelength_mid],
        kind="linear",
    )
    wavelength_FC_lambda = wavelength_FI_lambda.copy()
    flux_FC_lambda = F(wavelength_FC_lambda)

    return wavelength_FI_lambda, flux_FI_lambda, wavelength_FC_lambda, flux_FC_lambda


def compute_mean_flux(wavelength: np.ndarray, flux: np.ndarray) -> float:
    lambda_1 = np.min(wavelength)
    lambda_2 = np.max(wavelength)
    mean_flux = integrate.trapezoid(flux, wavelength) / (lambda_2 - lambda_1)
    return mean_flux


def extract_one_spectrum(
    wavelength: np.ndarray,
    flux: np.ndarray,
    index_band_start: float,
    index_band_end: float,
    func: callable = None,
) -> tuple[np.ndarray]:
    select_condition = (wavelength > index_band_start) & (wavelength < index_band_end)
    index_ = np.where(select_condition)[0]
    wavelength_intercept = wavelength[index_]
    flux_intercept = flux[index_]

    wavelength_intercept = np.concatenate(
        ([index_band_start], wavelength_intercept, [index_band_end])
    )

    flux_intercept = np.concatenate(
        ([func(index_band_start)], flux_intercept, [func(index_band_end)])
    )
    return wavelength_intercept, flux_intercept


def compute_EW(
    wavelength_FI_lambda, flux_FI_lambda, wavelength_FC_lambda, flux_FC_lambda
) -> float:
    return integrate.trapezoid(
        1 - (flux_FI_lambda / flux_FC_lambda), wavelength_FI_lambda
    )


def compute_Mag(
    wavelength_FI_lambda, flux_FI_lambda, wavelength_FC_lambda, flux_FC_lambda
) -> float:
    lambda_1 = np.min(wavelength_FI_lambda)
    lambda_2 = np.max(wavelength_FI_lambda)
    return -2.5 * np.log10(
        integrate.trapezoid(flux_FI_lambda / flux_FC_lambda, wavelength_FI_lambda)
        / (lambda_2 - lambda_1)
    )
