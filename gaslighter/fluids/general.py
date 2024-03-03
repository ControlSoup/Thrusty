import numpy as np


def mdot_equation(density: float, area: float, velocity: float):
    return density * area * velocity


def velocity_from_mdot(mdot: float, density: float, area: float):
    return mdot / (density * area)


def velocity_from_dh(h1: float, h2: float):
    """Kinetics, assumes loss in enthalpy goes to velocity"""
    return np.sqrt(2 * (h1 - h2))
