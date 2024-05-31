import numpy as np

from ..geometry import circle_area_from_diameter, circle_diameter_from_area
from ..math import np_poly

"""
Equations from Rocket Propulsion Elements 9th edition (Sutton)
"""


def thrust(mdot: float, velocity: float):

    return mdot * velocity


def exit_velocity(
    gamma: float,
    sp_R: float,
    chamber_pressure: float,
    combustion_temp: float,
    exit_pressure: float,
):
    """Eq 3-15b/16"""
    return np.sqrt(
        (2 * gamma / (gamma - 1))
        * sp_R
        * combustion_temp
        * (1 - (exit_pressure / chamber_pressure) ** ((gamma - 1) / gamma))
    )


def throat_area(cstar: float, chamber_pressure: float, mdot: float):
    """Eq 2-16"""
    return mdot * cstar / chamber_pressure


def throat_pressure(cstar: float, throat_area: float, mdot: float):
    """Eq 2-16 Re-aranged"""
    return mdot * cstar / throat_area


def critical_pressure(upstream_stagnation_pressure: float, gamma):
    return upstream_stagnation_pressure * (2 / (gamma + 1))**(gamma / (gamma - 1))


def half_angle_rad(throat_diameter: float, exit_length: float, exit_diameter: float):
    oppsite = (exit_diameter / 2.0) - (throat_diameter / 2.0)
    return np.arctan(oppsite / exit_length)


def eps(exit_area: float, throat_area: float):
    return exit_area / throat_area


def exit_length(throat_diameter: float, half_angle: float, exit_diameter: float):
    oppsite = (exit_diameter / 2.0) - (throat_diameter / 2.0)
    return oppsite / np.tan(half_angle)


def lstar(chamber_volume: float, throat_area: float):
    """Eq 8.9"""
    return chamber_volume / throat_area