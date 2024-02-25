from __future__ import annotations

import numpy as np

from ..units import convert
from .intensive_state import IntensiveState


# ------------------------------------------------------------------------------
# Functions to help with ideal gas analysis
# ------------------------------------------------------------------------------
def ideal_critical_pressure(upstrm_stag_press, upstream_gamma):
    """
    Source:
        https://en.wikipedia.org/wiki/Choked_flow
    """
    gamma_component = (2 / (upstream_gamma + 1)) ** (
        upstream_gamma / (upstream_gamma - 1)
    )
    ciritcal_press = upstrm_stag_press * gamma_component

    return ciritcal_press


def ideal_is_choked(upstream_presure, upstream_gamma, downstream_pressure):
    """
    Returns if the compressible fluid conditions are choked
    Source:
        https://en.wikipedia.org/wiki/Choked_flow
    """

    critical_press = ideal_critical_pressure(upstream_presure, upstream_gamma)

    return True if downstream_pressure < critical_press else False


def ideal_orifice_mdot(
    cda: float,
    upstream: IntensiveState,
    downstream_pressure: float,
    verbose_return: bool = False,
) -> float | tuple[float, bool]:
    """
    Source:
        https://en.wikipedia.org/wiki/Orifice_plate
    """

    # No flow under very low dp
    if upstream.pressure - downstream_pressure < 0.1:
        return 0.0

    is_choked = False

    if ideal_is_choked(upstream.pressure, upstream.gamma, downstream_pressure):
        # Choked flow equation
        gamma_choked_comp = (2 / (upstream.gamma + 1)) ** (
            (upstream.gamma + 1) / (upstream.gamma - 1)
        )
        mdot_kgps = cda * np.sqrt(
            upstream.gamma * upstream.density * upstream.pressure * gamma_choked_comp
        )

        is_choked = True
    else:
        # UnChoked flow equation
        gamma_UNchoked_comp = upstream.gamma / (upstream.gamma - 1)
        pressure_ideal1 = (downstream_pressure / upstream.pressure) ** (
            2 / upstream.gamma
        )
        pressure_ideal2 = (downstream_pressure / upstream.pressure) ** (
            (upstream.gamma + 1) / upstream.gamma
        )
        mdot_kgps = cda * np.sqrt(
            2
            * upstream.density
            * upstream.pressure
            * gamma_UNchoked_comp
            * (pressure_ideal1 - pressure_ideal2)
        )
    if verbose_return:
        return mdot_kgps, is_choked
    else:
        return mdot_kgps
