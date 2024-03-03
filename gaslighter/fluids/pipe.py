from CoolProp.CoolProp import PropsSI
from scipy.optimize import root_scalar

from ..geometry import circle_area_from_diameter
from .incompressible import (friction_factor, incompressible_orifice_mdot,
                             incompressible_pipe_dp, reynolds)
from .general import velocity_from_mdot
from .. import MIN_RESONABLE_DP_PA, MIN_RESONABLE_PRESSURE_PA


class IncompressiblePipe:
    def __init__(self, diameter: float, roughness: float, length: float, fluid: str):
        self.__diameter = diameter
        self.__area = circle_area_from_diameter(diameter)
        self.__roughness = roughness
        self.__relative_roughness = roughness / diameter
        self.__length = length
        self.__fluid = fluid

    def from_relative_roughness(
        hydraulic_diameter: float, relative_roughness: float, length: float, fluid
    ):
        return IncompressiblePipe(
            hydraulic_diameter, hydraulic_diameter * relative_roughness, length, fluid
        )

    @property
    def diameter(self):
        return self.__diameter

    @property
    def area(self):
        return self.__area

    @property
    def roughness(self):
        return self.__roughness

    @property
    def relative_roughness(self):
        return self.__relative_roughness

    @property
    def length(self):
        return self.__length

    @property
    def fluid(self):
        return self.__fluid

    def dp(
        self,
        mdot: float,
        upstream_press: float,
        upstream_temp: float,
        suppress_warning: bool = False,
    ):

        if upstream_press <= MIN_RESONABLE_PRESSURE_PA:
            return upstream_press

        # Fluid State
        density, dyn_viscosity = PropsSI(
            ["D", "V"], "P", upstream_press, "T", upstream_temp, self.__fluid
        )

        velocity = velocity_from_mdot(mdot, density, self.area) 

        re = reynolds(density, velocity, self.__diameter, dyn_viscosity)

        # Fricition factor
        ff = friction_factor(
            reynolds=re,
            relative_roughness=self.relative_roughness,
            suppress_warning=suppress_warning,
        )

        dp = incompressible_pipe_dp(
            self.__length, self.__diameter, density, velocity, ff
        )

        if dp > upstream_press:
            if not suppress_warning:
                print(f"WARNING| Dp is greater than upstream pressure [{dp} > {upstream_press}]")
            return upstream_press
        
        return dp

    def mdot(
        self, upstream_press: float, upstream_temp: float, downstream_press: float
    ):

        if upstream_press <= MIN_RESONABLE_DP_PA:
            return 0.0 

        # Fluid State
        density = PropsSI("D", "P", upstream_press, "T", upstream_temp, self.__fluid)

        # Root solve for mdot that makes dp error 0
        def dp_error(mdot):
            dp = self.dp(mdot, upstream_press, upstream_temp, suppress_warning=True)
            return (upstream_press - downstream_press) - dp

        # Use orifice flow as an intial guess
        orifice_mdot = incompressible_orifice_mdot(
            self.area, upstream_press, density, downstream_press
        )

        mdot_root = root_scalar(
            f=dp_error,
            x0=orifice_mdot,
            method="secant",
            xtol=1e-6,
            maxiter=200,
        )

        if not mdot_root.converged:
            raise ValueError(f"ERROR| {mdot_root}")

        return mdot_root.root