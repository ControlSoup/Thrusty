from CoolProp.CoolProp import PropsSI

from .. import MIN_RESONABLE_DP_PA, MIN_RESONABLE_PRESSURE_PA
from ..units import convert
from .general import velocity_from_mdot
from .incompressible import (
    incompressible_orifice_dp,
    incompressible_orifice_mdot,
    is_incompressible,
)
from . import dryer_injector_equations as dryer
from .intensive_state import IntensiveState
from .ideal_gas import ideal_orifice_mdot
from scipy.optimize import root_scalar


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
        suppress_warnings=False,
    ):

        if upstream_press <= MIN_RESONABLE_DP_PA:
            return upstream_press

        # Fluid State
        psat = PropsSI('P', 'T', upstream_temp, 'Q', 0.0, self.__fluid)

        if abs(psat - upstream_press) < 1e-4:
            density = PropsSI('D', 'P', upstream_press, 'Q', 0.0, self.__fluid)
        else:
            density = PropsSI("D", "P", upstream_press, "T", upstream_temp, self.__fluid)

        dp = incompressible_orifice_dp(self.__cda, density, mdot, self.__beta_ratio)

        if dp > upstream_press:
            if not suppress_warnings:
                print(
                    f"WARNING| Dp is greater than upstream pressure [{dp} > {upstream_press}]"
                )
            return upstream_press

        return dp

    def mdot(
        self,
        upstream_press: float,
        upstream_temp: float,
        downstream_press: float,
        suppress_warnings: bool = False,
    ):

        if upstream_press <= MIN_RESONABLE_PRESSURE_PA:
            return 0.0

        # Fluid State
        density, sos = PropsSI(
            ["D", "A"], "P", upstream_press, "T", upstream_temp, self.__fluid
        )

        mdot = incompressible_orifice_mdot(
            self.__cda, upstream_press, density, downstream_press, self.__beta_ratio
        )
        velocity = velocity_from_mdot(mdot, density, self.area)

        if not is_incompressible(velocity, sos):
            if not suppress_warnings:
                print(
                    f"WARNING| Fluid conditions may not be incompressible MACH: [{velocity / sos}] > 0.3"
                )

        return mdot

class DryerOrifice():

    def __init__(self, cd: float, area: float, fluid: str, beta_ratio=None):
        self.__cd = cd
        self.__area = area
        self.__cda = cd * area
        self.__cv = convert(self.__cda, "Cda_m2", "Cv")
        self.__fluid = fluid
        self.__beta_ratio = beta_ratio
        self.__k = 0.0
        self.__g_spi_mdot = 0.0
        self.__g_hem_mdot = 0.0
        self.__dryer_mdot = 0.0
        self.__incomp_velocity = 0.0

    def from_cda(cda: float, fluid: str, cd: float = 0.65, beta_ratio: float = None):
        return DryerOrifice(cd, cda / cd, fluid, beta_ratio)

    def from_cv(cv: float, fluid: str, cd: float = 0.65, beta_ratio: float = None):
        cda = convert(cv, "Cv", "Cda_m2")

        return DryerOrifice.from_cda(
            cda=cda, fluid=fluid, cd=cd, beta_ratio=beta_ratio
        )

    def dict(self, prefix: str = None):
        if prefix is None:
            prefix = ""
        else:
            prefix = f"{prefix}."
        
        return {
            f"{prefix}cd [-]": self.__cd, 
            f"{prefix}area [m^2]": self.__area, 
            f"{prefix}cda [m^2]": self.__cda, 
            f"{prefix}k [-]": self.__k, 
            f"{prefix}g_spi_mdot [kg/s]": self.__g_spi_mdot, 
            f"{prefix}incomp_velocity [m/s]": self.__incomp_velocity, 
            f"{prefix}g_hem_mdot [kg/s]": self.__g_hem_mdot, 
            f"{prefix}dyer_mdot [kg/s]": self.__dryer_mdot, 
        }

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

    def mdot(
        self,
        upstream_press: float,
        upstream_temp: float,
        downstream_press: float,
        suppress_warnings: bool = False,
        impose_liquid: bool = True
    ):
        """
        Source: Review and Evaluation of Models for Self-Pressurizing Propellant Tank Dynamics
        """
        if upstream_press <= MIN_RESONABLE_PRESSURE_PA:
            return 0.0

        # Upstream vapor pressure at current temperature
        upstream_vapor_pressure = PropsSI(
            'P',
            'T', upstream_temp,
            'Q', 1.0,
            self.__fluid
        )

        # State Lookup
        # Check if your close to saturation
        p_sat = PropsSI('P', 'T', upstream_temp, 'Q', 0.0, self.__fluid)
        if abs(p_sat - upstream_press) <= 1e-4:
            up_density, up_sp_enthalpy, up_sp_entropy = PropsSI(
                ['D', 'HMASS', 'SMASS'],
                'P', upstream_press,
                'Q', 0.0,
                self.__fluid
            )
        else:
            up_density, up_sp_enthalpy, up_sp_entropy = PropsSI(
                ['D', 'HMASS', 'SMASS'],
                'P', upstream_press,
                'T', upstream_temp,
                self.__fluid
            )

        # Isentropic expansion
        dwn_sp_enthalpy, dwn_density = PropsSI(
            ['HMASS', 'D'],
            'P', downstream_press,
            'SMASS', up_sp_entropy,
            self.__fluid
        )

        # Dryer method
        self.__k = dryer.k(
            upstream_press,
            upstream_vapor_pressure,
            downstream_press
        )


        g_spi = dryer.g_spi(
            upstream_press,
            up_density,
            downstream_press
        )
        self.__g_spi_mdot = self.cda * g_spi

        g_hem = dryer.g_hem(
            dwn_density,
            up_sp_enthalpy,
            dwn_sp_enthalpy
        )
        self.__g_hem_mdot = self.cda * g_hem 

        self.__dryer_mdot = dryer.dryer_mdot(self.cda, self.__k, g_spi, g_hem)

        self.__incomp_velocity = self.__g_spi_mdot / (up_density * self.area)

        return self.__dryer_mdot

    def dp(
        self,
        mdot: float,
        upstream_press: float,
        upstream_temp: float,
        suppress_warnings=False,
        max_dp = 10e10
    ):
        if mdot == 0.0:
            return 0.0

        def mdot_error(dp: float):

            new_mdot = self.mdot(upstream_press, upstream_temp, upstream_press - dp, suppress_warnings = True)

            return mdot - new_mdot

        dp_root = root_scalar(
            mdot_error,
            method='secant',
            x0 = incompressible_orifice_dp( # As a first guess assume saturated liquid conditions through an incompressible orifice
                self.cda,
                PropsSI('D', 'T', upstream_temp, 'Q', 0.0, self.fluid),
                mdot = mdot
            ),
            maxiter=1000,
            xtol=1e-6
        )

        if not dp_root.converged:
            if not suppress_warnings:
                raise ValueError(f"ROOT ERROR| {dp_root}")

        return dp_root.root


