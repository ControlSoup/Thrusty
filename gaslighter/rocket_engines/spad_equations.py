import numpy as np

"""
Equations from Space Propulsion Analysis and Design - Ronald W. Humble et al
"""


def min_wall(pressure: float, radius: float, tensile_ultimate: float):
    return pressure * radius / tensile_ultimate


def half_angle_losses(half_angle_rad: float):
    """Eq 3.151"""
    return (1 + np.cos(half_angle_rad)) / 2.0
