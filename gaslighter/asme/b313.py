""" Equations form B31.3
Source: ASME B31.3 (2002)
"""

import numpy as np
from scipy.optimize import root_scalar

from ..structrual.cylinder_stress import thin_wall_hoop_pressure
from ..units import convert


def pipe_pressure(
    thickness: float,
    outside_diameter: float,
    allowable_tensile: float,
    quality_factor: float = 0.8,
    thermal_coefficent: float = 0.4,
    thickness_percent_tolerance: float = 12.5,
):
    thickness_percent = 1 - (thickness_percent_tolerance /100)
    return (
        2
        * thickness
        * thickness_percent 
        * allowable_tensile
        * quality_factor
        / (outside_diameter - (2 * thickness * thermal_coefficent))
    )


def table_a1_stress(material: str, temp: int):
    material.upper()

    match material:
        case "COPPER":
            temp_array = convert(np.array([100, 150, 200, 250]), "degF", "degK")
            stress_array = convert(np.array([7.2, 6.7, 6.5, 6.3]) * 1000, "psia", "Pa")
        case _:
            raise ValueError(
                f"ERROR| No material data recorded for B31.3 Tabel A1 {material}"
            )

    for i, val in enumerate(temp_array):

        if i == len(temp) - 1:
            raise ValueError(
                f"ERROR| No stress data recorded for B31.3 TAble A1 {material} : > {val} [degK]"
            )

        if temp > val:
            continue

        return stress_array[i]
