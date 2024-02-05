import numpy as np
from gaslighter import STD_ATM_PA

def thrust(mdot: float, velocity: float):
    return mdot * velocity

def exit_velocity(gamma: float, sp_R: float, chamber_pressure: float, chamber_temp: float, exit_pressure: float):
    return np.sqrt(
        (2 * gamma / (gamma - 1)) * sp_R * chamber_temp
        * (1 - (exit_pressure / chamber_pressure)**((gamma - 1) / gamma))
    )
