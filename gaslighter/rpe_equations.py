import numpy as np
from gaslighter import circle_radius_from_area, circle_area_from_diameter

def thrust(mdot: float, velocity: float):

    return mdot * velocity

def exit_velocity(gamma: float, sp_R: float, chamber_pressure: float, combustion_temp: float, exit_pressure: float):
    ''' Eq 3-15b/16
    '''
    return np.sqrt(
        (2 * gamma / (gamma - 1)) * sp_R * combustion_temp
        * (1 - (exit_pressure / chamber_pressure)**((gamma - 1) / gamma))
    )

def throat_area(cstar, chamber_pressure, mdot):
    ''' Eq 2-16
    '''
    return mdot * cstar / chamber_pressure

def half_angle_rad(throat_diameter: float, exit_length: float, exit_diameter: float):
    oppsite = (exit_diameter / 2.0) - (throat_diameter / 2.0)
    return np.arctan(oppsite / exit_length)

def exit_length(throat_diameter: float, half_angle: float, exit_diameter: float):
    oppsite = (exit_diameter / 2.0) - (throat_diameter / 2.0)
    return oppsite / np.tan(half_angle)
