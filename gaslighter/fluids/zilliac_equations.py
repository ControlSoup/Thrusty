"""
Source:
    Review and Evaluation of Models for Self-Pressurizing Propellant Tank Dynamics [Jonah E. Zimmerman]
"""


def eq_11(sp_enthalpy: float, area: float, delta_t: float):
    return sp_enthalpy * area * delta_t


def eq_22(liquid_rho: float, vapor_rho: float, x: float, mtotal: float):
    return mtotal * (((1 - x) / liquid_rho) + (x / vapor_rho))


def eq_22_for_mtotal(liquid_rho: float, vapor_rho: float, x: float, volume: float):
    return volume / (((1 - x) / liquid_rho) + (x / vapor_rho))


def eq_23(
    total_sp_internal_energy: float,
    liquid_sp_internal_energy: float,
    vapor_sp_internal_energy: float,
):
    return (total_sp_internal_energy - liquid_sp_internal_energy) / (
        vapor_sp_internal_energy - liquid_sp_internal_energy
    )


def eq_24(mdot_evap: float, mdot_cond: float):
    return mdot_evap - mdot_cond


def eq_25(mdot_evap: float, mdot_cond: float, mdot_out: float):
    return -mdot_evap + mdot_cond - mdot_out


def eq_26(
    mdot_evap: float,
    sp_enthalpy_evap: float,
    mdot_cond: float,
    sp_enthalpy_cond: float,
    pressure: float,
    vdot_vapor: float,
    qdot_surf_vapor: float,
):
    return (
        (mdot_evap * sp_enthalpy_evap)
        - (mdot_cond * sp_enthalpy_cond)
        - (pressure * vdot_vapor)
        + qdot_surf_vapor
    )


def eq_27(
    mdot_out: float,
    sp_enthalpy_out: float,
    mdot_evap: float,
    sp_enthalpy_evap: float,
    mdot_cond: float,
    sp_enthalpy_cond: float,
    pressure: float,
    vdot_liquid: float,
    qdot_liquid_surf: float,
):
    return (
        -(mdot_out * sp_enthalpy_out)
        - (mdot_evap * sp_enthalpy_evap)
        + (mdot_cond * sp_enthalpy_cond)
        - (pressure * vdot_liquid)
        + qdot_liquid_surf
    )


def eq_28(
    qdot_liquid_surf: float,
    qdot_surf_vapor: float,
    enthalpy_of_vaporization: float,
    sat_liquid_sp_enthalpy: float,
    liquid_sp_enthalpy: float,
):
    return qdot_liquid_surf - qdot_surf_vapor / (
        enthalpy_of_vaporization + (sat_liquid_sp_enthalpy - liquid_sp_enthalpy)
    )


def eq_29(
    pressure: float,
    sat_pressure: float,
    vapor_volume: float,
    vapor_comp_factor: float,
    vapor_gas_trival_lookup: float,
    vapor_temp: float,
    dt: float,
):
    return (
        (pressure - sat_pressure)
        * vapor_volume
        / (vapor_comp_factor * vapor_gas_trival_lookup * vapor_temp * dt)
    )


def half_eq_32(
    pP_pT_from_rho: float, dTdt: float, pP_prho_from_T: float, drho_dt: float
):
    return (pP_pT_from_rho * dTdt) + (pP_prho_from_T * drho_dt)


def eq_35(
    cv: float,
    mass: float,
    dUdt: float,
    u: float,
    mdot: float,
    pu_pd_from_t: float,
    drho_dt: float,
):
    return ((dUdt - (u * mdot)) / mass) - (pu_pd_from_t * drho_dt) / cv


def eq_36(mdot: float, volume: float, mass: float, vdot: float):
    return mdot / volume - ((mass / volume**2) * vdot)
