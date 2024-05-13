import numpy as np

import warnings
from scipy.optimize import root_scalar
from .intensive_state import IntensiveState
from CoolProp.CoolProp import PropsSI

"""
Injector Modeling from: Modeling Feed System Flow Physics for Self-Pressurizing Propellants
Authors: Jonny Dyer, Eric Doran, Zach Dunn, and Kevin Lohner
"""


def g_hem(
    downstream_density: float,
    upstream_sp_enthalpy: float,
    downstream_sp_enthalpy: float,
):
    """Eq: 37 From Dryers 2phase injector model"""
    return downstream_density * np.sqrt(
        2 * (upstream_sp_enthalpy - downstream_sp_enthalpy)
    )


def g_spi(upstream_press: float, upstream_density: float, downstream_press: float):
    """Eq: 37 From Dryers 2phase injector model"""
    return np.sqrt(2 * upstream_density * (upstream_press - downstream_press))


def k(
    upstream_press: float,
    upstream_vapor_pressure: float,
    downstream_press: float,
):
    """Eq: 35 From Dryers 2phase injector model"""
    return np.sqrt(
        (upstream_press - downstream_press)
        / (upstream_vapor_pressure - downstream_press)
    )


def dryer_mdot(cda: float, k: float, g_spi: float, g_hem: float):
    """Eq: 36 From Dryers 2phase injector model (Solomon Correction)"""
    return cda * ((k * g_spi) + g_hem) / (1 + k)

def complete_dryer_mdot(
    cda: float,
    upstream_state: IntensiveState,
    downstream_press: float,
    suppress_warnings: bool = False,
):
    """
    Source: Review and Evaluation of Models for Self-Pressurizing Propellant Tank Dynamics
    """

    pmin = PropsSI("PMIN", upstream_state)
    if upstream_state.press <= pmin:
        if not suppress_warnings:
            warnings.warn(
                f"WARNING| Upstream pressure is less than PMIN = {np.round(pmin, 2)} Pa"
            )
        return 0.0

    # Upstream vapor pressure at current temperature
    upstream_vapor_pressure = PropsSI(
        "P", 
        "T", upstream_state.temp, 
        "Q", 1.0, 
        upstream_state.fluid
    )

    # Isentropic expansion
    dwn_sp_enthalpy, dwn_density = PropsSI(
        ["HMASS", "D"], 
        "P", downstream_press, 
        "SMASS", upstream_state.sp_entropy, 
        upstream_state.fluid
    )

    # Dryer method
    _k = k(
        upstream_press=upstream_state.pressure, 
        upstream_vapor_pressure=upstream_vapor_pressure, 
        downstream_press=downstream_press
    )

    _g_spi = g_spi(
        upstream_press=upstream_state.pressure, 
        upstream_density=upstream_state.density, 
        downstream_press=downstream_press
    )

    _g_hem = g_hem(
        downstream_density=dwn_density, 
        upstream_sp_enthalpy=upstream_state.sp_enthalpy, 
        downstream_sp_enthalpy=dwn_sp_enthalpy
    )

    return dryer_mdot(cda, _k, _g_spi, _g_hem)

def complete_dryer_cda(
    mdot: float,
    upstream: IntensiveState,
    downstream_press: float,
):

    def area_error(area):
        return mdot - complete_dryer_mdot(area, upstream, downstream_press)

    root = root_scalar(area_error, method="secant", x0=1, maxiter=500, xtol=1e-6)

    if not root.converged:
        raise ValueError(f"ROOT ERROR|{root}")

    return root.root