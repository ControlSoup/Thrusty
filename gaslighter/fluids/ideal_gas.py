from __future__ import annotations

import numpy as np

from .intensive_state import IntensiveState
from scipy.optimize import root_scalar


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


def ideal_is_choked(upstream_presure, upstream_gamma, downstream_press):
    """
    Returns if the compressible fluid conditions are choked
    Source:
        https://en.wikipedia.org/wiki/Choked_flow
    """

    critical_press = ideal_critical_pressure(upstream_presure, upstream_gamma)

    return True if downstream_press < critical_press else False


def ideal_orifice_mdot(
    cda: float,
    upstream: IntensiveState,
    downstream_press: float,
    verbose_return: bool = False,
) -> float | tuple[float, bool]:
    """
    Source:
        https://en.wikipedia.org/wiki/Orifice_plate
    """

    # No flow under very low dp
    if upstream.pressure - downstream_press < 0.1:
        if verbose_return:
            return 0.0, False
        return 0.0

    is_choked = False

    if ideal_is_choked(upstream.pressure, upstream.gamma, downstream_press):
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
        pressure_ideal1 = (downstream_press / upstream.pressure) ** (2 / upstream.gamma)
        pressure_ideal2 = (downstream_press / upstream.pressure) ** (
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

    return mdot_kgps


def ideal_orifice_cda(
    mdot: float,
    upstream: IntensiveState,
    downstream_press: float,
    verbose_return: bool = False,
):

    def area_error(area):
        return mdot - ideal_orifice_mdot(area, upstream, downstream_press)

    root = root_scalar(area_error, method="secant", x0=1, maxiter=500, xtol=1e-6)

    if not root.converged:
        raise ValueError(f"ROOT ERROR|{root}")

    cda = root.root

    if verbose_return:
        return cda, ideal_is_choked(
            upstream_presure=upstream.pressure,
            upstream_gamma=upstream.gamma,
            upstream=downstream_press,
        )

    else:
        return cda
