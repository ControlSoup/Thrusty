import numpy as np
from scipy.optimize import root_scalar


"""
Sources:
    - Pipe Flow [Donald C. Rennels]
    - Critical Reynolds / turblant transition was bassically made up idk man
"""

def is_incompressible(velocity: float, sos: float):
    """https://courses.ansys.com/wp-content/uploads/2020/12/Compressible-Flow-regimes-Lesson-4-Handout.pdf"""
    mach_number = velocity / sos

    if mach_number < 0.3:
        return True

    return False

def reynolds(
    denisty: float, velocity: float, char_length: float, dynamic_viscosity: float
):
    return denisty * velocity * char_length / dynamic_viscosity


def jain_forumulation(reynolds: float, relative_roughness: float):
    """Jain Forumulation of the colebrook equation (within 3%)"""
    return (2 * np.log10((relative_roughness / 3.7) + (6.97 / reynolds))) ** -2


def colebrook_solution(reynolds: float, relative_roughness: float):
    """Returns a colebrook friction factor using the secant method"""

    def colebrook(ff: float):
        return (
            -2
            * np.log10((2.51 / (reynolds * np.sqrt(ff))) + (relative_roughness / 3.71))
        ) - 1.0 / np.sqrt(ff)

    ff_root_result = root_scalar(
        colebrook,
        x0=jain_forumulation(reynolds, relative_roughness),  # Use jain as first guess
        method="secant",
        xtol=1e-6,
        maxiter=300,
    )

    if not ff_root_result.converged:
        raise ValueError(f"ERROR| {ff_root_result}")

    return ff_root_result.root


def friction_factor(
    reynolds: float, relative_roughness: float, suppress_warnings: bool = False
):
    """Returns a friction factor depending on flow regieme"""

    laminar_re = 2320
    turbulant_re = 3500

    # Laminar Solution
    if reynolds <= laminar_re:
        return 64 / reynolds

    # Turbulant Colebrook ( I can't find concrete sources for these numbers)
    if reynolds >= 3500:
        return colebrook_solution(reynolds, relative_roughness)

    # Transition Zone
    else:
        if not suppress_warnings:
            print("WARNING| Friction factor is in transition zone")

        ff_laminar = 64 / reynolds
        ff_turbulant = colebrook_solution(reynolds, relative_roughness)

        ratio = (reynolds - laminar_re) / (turbulant_re - laminar_re)

        return (ff_laminar * (1 - ratio)) + (ff_turbulant * ratio)


def incompressible_pipe_dp(
    length: float,
    hydraulic_diameter: float,
    density: float,
    flow_velocity: float,
    friciton_factor: float,
):
    """Darcy Weibech head loss, converted to pressure drop"""

    return (
        (length * friciton_factor * density * flow_velocity**2) / (2 * hydraulic_diameter)
    )


def incompressible_orifice_mdot(
    cda: float,
    upstream_press: float,
    upstream_density: float,
    downstream_pressure: float,
    beta_ratio: float = None,
):
    """Incompressible Cda Orifice Flow Equation"""
    # Beta correction factor formula
    beta_comp = 1

    if beta_ratio is not None:
        beta_comp = np.sqrt(1 - beta_ratio**4)

    return cda * np.sqrt(2 * upstream_density * (upstream_press - downstream_pressure))


def incompressible_orifice_dp(
    cda: float,
    upstream_density: float,
    mdot: float,
    beta_ratio: float = None,
):
    """Incompressible Cda Orifice flow equation, solved for Dp"""
    # Beta correction factor formula
    beta_comp = 1

    if beta_ratio is not None:
        beta_comp = np.sqrt(1 - beta_ratio**4)

    return (mdot * beta_comp / cda) ** 2 / (2.0 * upstream_density)
