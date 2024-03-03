from __future__ import annotations

import numpy as np
from CoolProp.CoolProp import PropsSI
from scipy.optimize import root_scalar

from .intensive_state import IntensiveState
from .general import mdot_equation



def gas_velocity(sp_enthalpy_1: float, sp_enthalpy_2: float):
    return np.sqrt(2 * (sp_enthalpy_1 - sp_enthalpy_2))


class Throat:
    def __init__(self, sp_entropy: float, pressure: float, fluid: str):
        self.sp_enthalpy = PropsSI("HMASS", "SMASS", sp_entropy, "P", pressure, fluid)
        self.density = PropsSI("D", "SMASS", sp_entropy, "P", pressure, fluid)
        self.speed_of_sound = PropsSI("A", "SMASS", sp_entropy, "P", pressure, fluid)


def real_orifice_mdot(
    cda: float,
    upstream: IntensiveState,
    downstream_pressure: float,
    verbose_return: bool = False,
) -> float | tuple[float, bool]:

    # Ignore low dp
    if upstream.pressure - downstream_pressure <= 0.1:
        if verbose_return:
            return 0.0, False
        return 0.0

    # Flow is choked under very high presure ratios
    if upstream.pressure / downstream_pressure > 5.0:
        is_choked = True

    # Assume unchoked is plausable
    else:
        # Isentropic expansion, matching downstream conditions
        throat = Throat(upstream.sp_entropy, downstream_pressure, upstream.fluid)

        throat_vel = gas_velocity(upstream.sp_enthalpy, throat.sp_enthalpy)

        # Check if flow is subsonic or exactly choked
        if throat_vel <= throat.speed_of_sound:
            mdot = mdot_equation(throat.density, cda, throat_vel)
            is_choked = False
        else:
            is_choked = True

    if is_choked:

        def sonic_error(throat_pressure: float):
            """
            Creates a functions whos root is the pressure at which
            throat is mach 1
            """
            sonic_throat = Throat(upstream.sp_entropy, throat_pressure, upstream.fluid)
            sonic_throat_vel = gas_velocity(
                upstream.sp_enthalpy, sonic_throat.sp_enthalpy
            )

            return sonic_throat.speed_of_sound - sonic_throat_vel

        # Root solve for mach 1 throat
        throat_pressure_root_result = root_scalar(
            f=sonic_error,
            x0=upstream.pressure / 2.0,  # Choked pressure ratio guesss
            bracket=[downstream_pressure, upstream.pressure],
            method="secant",
            xtol=1e-6,
            maxiter=200,
        )

        if not throat_pressure_root_result.converged:
            raise ValueError(f"ERROR| {throat_pressure_root_result}")

        throat = Throat(
            upstream.sp_entropy, throat_pressure_root_result.root, upstream.fluid
        )
        throat_vel = gas_velocity(upstream.sp_enthalpy, throat.sp_enthalpy)

        mdot = mdot_equation(throat.density, cda, throat_vel)

    if verbose_return:
        return mdot, is_choked

    return mdot
