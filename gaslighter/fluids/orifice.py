from CoolProp.CoolProp import PropsSI

from ..units import convert
from .incompressible import (
    incompressible_orifice_dp,
    incompressible_orifice_mdot, 
    is_incompressible
)
from .general import velocity_from_mdot
from .. import MIN_RESONABLE_DP_PA, MIN_RESONABLE_PRESSURE_PA

class IncompressibleOrifice:
    def __init__(self, cd: float, area: float, fluid: str, beta_ratio=None):
        self.__cd = cd
        self.__area = area
        self.__cda = cd * area
        self.__cv = convert(self.__cda, "Cda_m2", "Cv")
        self.__fluid = fluid
        self.__beta_ratio = beta_ratio

    def from_cda(cda: float, fluid: str, cd: float = 0.65, beta_ratio: float = None):
        return IncompressibleOrifice(cd, cda / cd, fluid, beta_ratio)

    def from_cv(cv: float, fluid: str, cd: float = 0.65, beta_ratio: float = None):
        cda = convert(cv, "Cv", "Cda_m2")

        return IncompressibleOrifice.from_cda(
            cda=cda, fluid=fluid, cd=cd, beta_ratio=beta_ratio
        )

    @property
    def cd(self):
        return self.__cd

    @property
    def area(self):
        return self.__area

    @property
    def cda(self):
        return self.__cda

    @property
    def cv(self):
        return self.__cv

    @property
    def beta_ratio(self):
        return self.__beta_ratio

    @property
    def fluid(self):
        return self.__fluid

    def dp(
        self, 
        mdot: float, 
        upstream_press: float, 
        upstream_temp: float, 
        suppress_warnings=False
    ):

        if upstream_press <= MIN_RESONABLE_DP_PA:
            return upstream_press

        # Fluid State
        density = PropsSI("D", "P", upstream_press, "T", upstream_temp, self.__fluid)

        dp = incompressible_orifice_dp(self.__cda, density, mdot, self.__beta_ratio)

        if dp > upstream_press:
            if not suppress_warnings:
                print(f"WARNING| Dp is greater than upstream pressure [{dp} > {upstream_press}]")
            return upstream_press
        
        return dp

    def mdot(
        self, 
        upstream_press: float, 
        upstream_temp: float, 
        downstream_press: float,
        suppress_warnings: bool = False
    ):

        if upstream_press <= MIN_RESONABLE_PRESSURE_PA:
            return 0.0 

        # Fluid State
        density, sos = PropsSI(["D","A"], "P", upstream_press, "T", upstream_temp, self.__fluid)

        mdot =  incompressible_orifice_mdot(
            self.__cda, upstream_press, density, downstream_press, self.__beta_ratio
        )
        velocity = velocity_from_mdot(mdot, density, self.area)

        if not is_incompressible(velocity, sos):
            if not suppress_warnings:
                print(f"WARNING| Fluid conditions may not be incompressible MACH: [{velocity / sos}] > 0.3")

        return mdot