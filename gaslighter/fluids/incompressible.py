import numpy as np
from scipy.optimize import root_scalar

"""
Sources:
    - Pipe Flow [Donald C. Rennels]
    - Critical Reynolds was bassically made up idk man
"""


CRITICAL_REYNOLDS = 2320


def friction_factor(reynolds: float, relative_roughness: float, diameter: float):

    # Laminar Solution
    if reynolds < CRITICAL_REYNOLDS:
        return 64 / reynolds

    # Turbulant Colebrook
    else:

        def colebrook(ff: float):
            return (
                -2
                * (
                    np.log10(
                        (relative_roughness / (3.7 * diameter))
                        + (2.51 / (reynolds * np.sqrt(ff)))
                    )
                )
                * np.sqrt(ff)
            ) - 1

        ff_root_result = root_scalar(
            colebrook,
            x0=64 / reynolds,  # Laminar guess
            method="secant",
            xtol=1e-6,
            maxiter=200,
        )

        if not ff_root_result.converged:
            raise ValueError(f"ERROR| {ff_root_result}")

        return ff_root_result.root


def incompressible_pipe_dp(
    length: float,
    hydraulic_diameter: float,
    density: float,
    flow_velocity: float,
    friciton_factor: float,
):
    return (
        length * friciton_factor * density * flow_velocity**2 / (2 * hydraulic_diameter)
    )


def incompressible_orifice_mdot(
    cda: float,
    upstream_pressure: float,
    upstream_density: float,
    downstream_pressure: float,
    beta_ratio: float = np.inf,
):
    return (
        cda
        / (np.sqrt(1 - beta_ratio**4))
        * np.sqrt(2 * upstream_density * (upstream_pressure - downstream_pressure))
    )


def incompressible_orifice_dp(
    cda: float,
    upstream_density: float,
    mdot: float,
    beta_ratio: float = np.inf,
):
    return (mdot * (np.sqrt(1 - beta_ratio**4)) / cda) ** 2 / (2.0 * upstream_density)
