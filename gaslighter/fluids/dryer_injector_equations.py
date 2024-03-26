from CoolProp.CoolProp import PropsSI
import numpy as np
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
    return downstream_density * np.sqrt(2 * (upstream_sp_enthalpy - downstream_sp_enthalpy))

def g_spi(
    upstream_press: float,
    upstream_density: float,
    downstream_press: float
):
    """Eq: 37 From Dryers 2phase injector model"""
    return np.sqrt(2 * upstream_density * (upstream_press - downstream_press))

def k(
    upstream_press: float,
    upstream_vapor_pressure: float,
    downstream_press: float,
):
    """Eq: 35 From Dryers 2phase injector model"""
    return np.sqrt((upstream_press - downstream_press) / (upstream_vapor_pressure - downstream_press))

def dryer_mdot(
    cda: float,
    k: float,
    g_spi: float,
    g_hem: float
):
    """Eq: 36 From Dryers 2phase injector model (Solomon Correction)"""
    return cda * ((k * g_spi) + g_hem) / (1 + k)

