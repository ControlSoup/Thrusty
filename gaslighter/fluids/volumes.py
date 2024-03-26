from CoolProp.CoolProp import PropsSI
from scipy.optimize import root_scalar

from .. import MIN_RESONABLE_PRESSURE_PA, pretty_dict
from ..errors import check_float, check_str
from ..integration import np_rk4
from . import zilliac_equations as zilliac
from .intensive_state import IntensiveState, look_from_quality


# Very bare bones data containter for volume
class BasicStaticVolume:

    def __init__(self, mass: float, volume: float, inenergy: float, fluid: str):

        check_float(mass)
        check_float(volume)
        check_float(inenergy)
        check_str(fluid)

        self.__mass = mass
        self.__volume = volume
        self.__inenergy = inenergy
        self.state = IntensiveState(
            "D",
            self.__mass / self.__volume,
            "UMASS",
            self.__inenergy / self.__mass,
            fluid,
        )

    @property
    def mass(self):
        return self.__mass

    @property
    def volume(self):
        return self.__volume

    @property
    def inenergy(self):
        return self.__inenergy

    def from_ptv(pressure: float, temp: float, volume: float, fluid: float):

        check_float(pressure)
        check_float(temp)
        check_float(volume)
        check_str(fluid)
        state = IntensiveState("P", pressure, "T", temp, fluid)
        mass = state.density * volume
        return BasicStaticVolume(mass, volume, state.sp_inenergy * mass, fluid)

    def update_mu(self, mass: float, inenergy: float):

        check_float(mass)
        check_float(inenergy)

        self.__mass = mass
        self.__inenergy = inenergy

        self.state.update_from_du(
            self.__mass / self.__volume, self.__inenergy / self.__mass
        )


class EquilibrumTank:
    def __init__(self, starting_pressure: float, volume: float, fluid: float):
        """
        Assumptions:
            - No heat transfer from the walls
            - Assumes starting volume is saturated liquid

        Source:
            Review and Evaluation of Models for Self-Pressurizing Propellant Tank Dynamics [Jonah E. Zimmerman]

        Note: ALL CONTENTS OF THIS CLASS ARE NOT INTENDED FOR EXTERNAL MODIFICATON
        """
        self.fluid = fluid
        self.volume = volume
        self.pressure = starting_pressure
        self.temp = PropsSI("T", "P", self.pressure, "Q", 0.0, self.fluid)
        self.liquid_sat_sp_inenergy = PropsSI(
            "UMASS", "T", self.temp, "Q", 0.0, self.fluid
        )
        self.liquid_sat_density = PropsSI("D", "T", self.temp, "Q", 0.0, self.fluid)

        self.vapor_sat_sp_inenergy = PropsSI(
            "UMASS", "T", self.temp, "Q", 1.0, self.fluid
        )
        self.vapor_sat_density = PropsSI("D", "T", self.temp, "Q", 1.0, self.fluid)

        self.x = zilliac.eq_23(
            self.liquid_sat_sp_inenergy,  # Start by assuming liquid
            self.liquid_sat_sp_inenergy,
            self.vapor_sat_sp_inenergy,
        )
        self.total_mass = zilliac.eq_22_for_mtotal(
            self.liquid_sat_density, self.vapor_sat_density, self.x, self.volume
        )
        self.total_inenergy = self.total_mass * self.liquid_sat_sp_inenergy

        # State Equations
        self.total_mdot = 0.0
        self.total_inenergy_dot = 0.0

    def from_mass(starting_pressure: float, mass: float, fluid: float):

        temp = PropsSI("T", "P", starting_pressure, "Q", 0.0, fluid)
        liquid_sat_sp_inenergy = PropsSI("UMASS", "T", temp, "Q", 0.0, fluid)
        liquid_sat_density = PropsSI("D", "T", temp, "Q", 0.0, fluid)
        vapor_sat_sp_inenergy = PropsSI("UMASS", "T", temp, "Q", 1.0, fluid)
        vapor_sat_density = PropsSI("D", "T", temp, "Q", 1.0, fluid)

        x = zilliac.eq_23(
            liquid_sat_sp_inenergy, liquid_sat_sp_inenergy, vapor_sat_sp_inenergy
        )
        volume = zilliac.eq_22(
            liquid_sat_density,
            vapor_sat_density,
            x=x,
            mtotal=mass,
        )

        return EquilibrumTank(starting_pressure, volume, fluid)

    def dict(self, prefix: str = None):

        if prefix is None:
            prefix = ""
        else:
            prefix = f"{prefix}."

        return {
            f"{prefix}volume [m^3]": self.volume,
            f"{prefix}pressure [Pa]": self.pressure,
            f"{prefix}temp [degK]": self.temp,
            f"{prefix}liq_sp_intenergy [J/kg]": self.liquid_sat_sp_inenergy,
            f"{prefix}liquid_sat_density [kg/m^3]": self.liquid_sat_density,
            f"{prefix}vapor_sat_sp_inenergy [J/kg]": self.vapor_sat_sp_inenergy,
            f"{prefix}vapor_sat_density [kg/m^3]": self.vapor_sat_density,
            f"{prefix}x [-]": self.x,
            f"{prefix}total_mass [kg]": self.total_mass,
            f"{prefix}total_inenergy [J]": self.total_inenergy,
            f"{prefix}total_mdot [kg/s]": self.total_mdot,
            f"{prefix}total_inenergy_dot [J/s]": self.total_inenergy_dot,
        }

    def integrate_state(
        self, mdot_out: float, dt: float, suppress_warning: bool = False
    ):

        if dt == 0.0:
            return None

        if self.total_mass <= 0.0:
            print("WARNING| Total Mass in tank is 0.0")
            return None

        # Total total_mdot [Eq 20]
        self.total_mdot = -mdot_out

        # Internal energy is a function of mass flow and enthalpy [Eq 21]
        # it is assumed saturated liquid is exiting the tank wich is a huge limitation
        self.total_inenergy_dot = -mdot_out * PropsSI(
            "HMASS", "P", self.pressure, "Q", 0.0, self.fluid
        )

        # Integrate state
        self.total_mass = np_rk4([self.total_mdot, self.total_mass], dt)
        self.total_inenergy = np_rk4([self.total_inenergy_dot, self.total_inenergy], dt)

        # Solve for a saturated T that works for the volume constraint [Eq (22, 23)]
        def volume_constraint(temp: float):
            self.liquid_sat_density, self.liquid_sat_sp_inenergy = PropsSI(
                ["D", "UMASS"], "T", temp, "Q", 0.0, self.fluid
            )
            self.vapor_sat_density, self.vapor_sat_sp_inenergy = PropsSI(
                ["D", "UMASS"], "T", temp, "Q", 1.0, self.fluid
            )

            self.x = zilliac.eq_23(
                self.total_inenergy / self.total_mass,
                self.liquid_sat_sp_inenergy,
                self.vapor_sat_sp_inenergy,
            )
            calc_volume = zilliac.eq_22(
                self.liquid_sat_density, self.vapor_sat_density, self.x, self.total_mass
            )

            return calc_volume - self.volume

        temp_result = root_scalar(
            volume_constraint,
            method="secant",
            x0=self.temp,
            bracket=[PropsSI("TMIN", "N2O"), PropsSI("TMAX", "N2O")],
            maxiter=1000,
            xtol=1e-6,
        )

        if not temp_result.converged:
            if not suppress_warning:
                raise ValueError(f"ROOT ERROR| {temp_result}")

        self.temp = temp_result.root
        self.pressure = PropsSI("P", "T", self.temp, "Q", 0.0, self.fluid)


# There some errors with this that need work, go pretty close those
# class ZillacKarabeyogluVolume:
# def __init__(
#     self,
#     fill_fraction: float,
#     pressure: float,
#     starting_temp: float,
#     volume: float,
#     tank_area: float,
#     fluid: float,
#     emperial_correction: float = 10e3
# ):
#     '''
#     Assumptions:
#         - No heat transfer from the walls

#     Source:
#         Review and Evaluation of Models for Self-Pressurizing Propellant Tank Dynamics [Jonah E. Zimmerman]

#     Note: ALL CONTENTS OF THIS CLASS ARE NOT INTENDED FOR EXTERNAL MODIFICATON
#     '''
#     self.fill_fraction = fill_fraction
#     self.fluid = fluid

#     self.pressure = pressure
#     self.volume = volume
#     self.tank_area = tank_area
#     self.e = emperial_correction

#     self.liquid_volume = fill_fraction * volume
#     self.liquid_state = IntensiveState('P', pressure, 'T', starting_temp, fluid)
#     self.liquid_mass = self.liquid_volume * self.liquid_state.density

#     self.vapor_volume = self.volume - self.liquid_volume
#     self.vapor_state = IntensiveState('P', pressure, 'T', starting_temp, fluid)
#     self.vapor_mass = self.volume * self.vapor_state.density

#     self.mdot_out = 0.0
#     self.mdot_evap = 0.0
#     self.mdot_cond = 0.0

#     self.latent_heat = 0.0

#     self.vapor_sat_sp_enthalpy = 0.0
#     self.vapor_sat_pressure = 0.0
#     self.liquid_sat_sp_enthalpy = 0.0
#     self.latent_heat = 0.0

#     # Equations of state
#     self.qdot_liquid_surf = 0.0
#     self.qdot_surf_vapor = 0.0

#     self.mdot_vapor = 0.0
#     self.vapor_internal_energy_dot = 0.0

#     self.mdot_liquid = 0.0
#     self.liquid_internal_energy_dot = 0.0

#     self.vapor_rhodot = 0.0
#     self.liquid_rhodot = 0.0

#     self.vapor_tdot = 0.0
#     self.liquid_tdot = 0.0

#     self.pressure_balance_vapor = 0.0
#     self.pressure_balance_liquid = 0.0

# def dict(self, prefix: str = None):

#     if prefix is not None:
#         prefix = f"{prefix}."
#     else:
#         prefix = ""

#     return{
#         f"{prefix}fill_fraction [-]": self.fill_fraction,
#         f"{prefix}pressure [Pa]": self.pressure,
#         f"{prefix}total_volume [m^3]": self.volume,
#         f"{prefix}area [m^2]": self.tank_area,
#         f"{prefix}e [-]": self.e,
#         f"{prefix}liquid_volume [m^3]": self.liquid_volume,
#         f"{prefix}liquid_mass [kg]": self.liquid_mass,
#         f"{prefix}vapor_volume [m^3]": self.vapor_volume,
#         f"{prefix}vapor_mass [kg]": self.vapor_mass,
#         f"{prefix}mdot_out [kg/s]": self.mdot_out,
#         f"{prefix}mdot_evap [kg/s]": self.mdot_evap,
#         f"{prefix}mdot_cond [kg/s]": self.mdot_cond,
#         f"{prefix}qdot_liquid_surf [J/s]": self.qdot_liquid_surf,
#         f"{prefix}qdot_sruf_vapor [J/s]": self.qdot_surf_vapor,
#         f"{prefix}mdot_vapor [kg/s]": self.mdot_vapor,
#         f"{prefix}vapor_internal_energy_dot [J/s]": self.vapor_internal_energy_dot,
#         f"{prefix}mdot_liquid [kg/s]": self.mdot_liquid,
#         f"{prefix}liquid_internal_energy_dot[J/s]": self.liquid_internal_energy_dot,
#         f"{prefix}vapor_rhodot [kg/(m^3*s)]": self.vapor_rhodot,
#         f"{prefix}liquid_rhodot [kg/(m^3*s)]": self.liquid_rhodot,
#         f"{prefix}vapor_tdot [degK/s]": self.vapor_tdot,
#         f"{prefix}liquid_tdot [degK/s]": self.liquid_tdot,
#         f"{prefix}pressure_balance_vapor [-]": self.pressure_balance_vapor,
#         f"{prefix}pressure_balance_liquid [-]": self.pressure_balance_liquid,
#         f"{prefix}vapor_sat_sp_enthalpy [J/kg]": self.vapor_sat_sp_enthalpy,
#         f"{prefix}vapor_sat_pressure [Pa]": self.vapor_sat_pressure,
#         f"{prefix}liquid_sat_sp_ethalpy [J/kg]": self.liquid_sat_sp_enthalpy,
#         f"{prefix}latent_heat [J/kg]": self.latent_heat,
#     }


# def integrate_state(self, mdot_out: float, dt: float, suppress_warning = False):

#     if dt <= 0.0:
#         return None

#     self.mdot_out = mdot_out

#     # Saturation lookups
#     self.vapor_sat_sp_enthalpy = look_from_quality('HMASS','P',self.pressure, 1.0, self.fluid)
#     self.vapor_sat_pressure = look_from_quality('P', 'T', self.vapor_state.temp, 1.0, self.fluid)
#     self.liquid_sat_sp_enthalpy = look_from_quality('HMASS', 'P', self.pressure, 0.0, self.fluid)
#     self.latent_heat = self.vapor_sat_sp_enthalpy - self.liquid_sat_sp_enthalpy

#     # Heat transfer
#     self.qdot_liquid_surf = self.e * zilliac.eq_11(
#         self.liquid_state.sp_enthalpy,
#         self.tank_area,
#         (self.vapor_state.temp - self.liquid_state.temp)
#     )
#     self.qdot_sruf_vapor = zilliac.eq_11(
#         self.vapor_state.sp_enthalpy,
#         self.tank_area,
#         (self.liquid_state.temp - self.vapor_state.temp)
#     )

#     # Evaporation Mdot
#     self.mdot_evap = zilliac.eq_28(
#         self.qdot_liquid_surf,
#         self.qdot_surf_vapor,
#         self.latent_heat,
#         self.liquid_sat_sp_enthalpy,
#         self.liquid_state.sp_enthalpy
#     )

#     # Eq 29 [Condensation: Vapor into Liquid]
#     # I tried to use a density lookup method here (but it fails.... :(
#     if self.pressure > self.vapor_sat_pressure:

#         # def pressure_error(density: float):
#         #     new_vapor_pressure = PropsSI('P', 'D', density, 'T', self.vapor_state.temp, self.fluid)

#         #     return self.vapor_sat_pressure - new_vapor_pressure

#         # density_root = root_scalar(
#         #     pressure_error,
#         #     method='secant',
#         #     x0 = self.vapor_state.density,
#         #     maxiter=500
#         # )

#         # if not density_root.converged:
#         #     if not suppress_warning:
#         #         raise ValueError(f"ROOT ERROR| {density_root}")

#         # # total_mdot = d_rho/dt * V [for constant volume]
#         # self.mdot_cond = (density_root.root - self.vapor_state.density) / dt * self.vapor_volume

#         # self.mdot_cond = zilliac.eq_29(
#         #     self.pressure,
#         #     self.vapor_sat_pressure,
#         #     self.vapor_volume,
#         #     self.vapor_state.lookup('Z'),
#         #     self.vapor_state.lookup('GAS_CONSTANT'),
#         #     self.vapor_state.temp,
#         #     dt
#         # )
#         self.mdot_cond = 0.0


#     else:
#         self.mdot_cond = 0.0


#     # Mdots
#     self.mdot_vapor = zilliac.eq_24(self.mdot_evap, self.mdot_cond)
#     self.mdot_liquid = zilliac.eq_25(self.mdot_evap, self.mdot_cond, self.mdot_out)

#     # Solve for Vdot
#     def pressure_balance(vdot_liquid):
#         # Eq 26, 27
#         self.vapor_internal_energy_dot = zilliac.eq_26(
#             self.mdot_evap, self.vapor_state.sp_enthalpy,
#             self.mdot_cond, self.liquid_state.sp_enthalpy,
#             self.pressure,
#             -vdot_liquid,
#             self.qdot_surf_vapor
#         )
#         self.liquid_internal_energy_dot = zilliac.eq_27(
#             self.mdot_out, self.liquid_state.sp_enthalpy,
#             self.mdot_evap, self.liquid_state.sp_enthalpy,
#             self.mdot_cond, self.vapor_state.sp_inenergy,
#             self.pressure,
#             vdot_liquid,
#             self.qdot_liquid_surf
#         )

#         # Eq 37
#         self.vapor_rhodot = zilliac.eq_36(
#             self.mdot_vapor,
#             self.vapor_volume,
#             self.vapor_mass,
#             -vdot_liquid
#         )
#         self.liquid_rhodot = zilliac.eq_36(
#             self.mdot_liquid,
#             self.liquid_volume,
#             self.liquid_mass,
#             vdot_liquid
#         )

#         # Eq 35
#         self.vapor_tdot = zilliac.eq_35(
#             self.vapor_state.cv,
#             self.vapor_mass,
#             self.vapor_internal_energy_dot,
#             self.vapor_state.sp_inenergy,
#             self.mdot_vapor,
#             pu_pd_from_t = self.vapor_state.lookup('d(U)/d(D)|T'),
#             drho_dt=self.vapor_rhodot
#         )
#         self.vapor_tdot = zilliac.eq_35(
#             self.liquid_state.cv,
#             self.liquid_mass,
#             self.liquid_internal_energy_dot,
#             self.liquid_state.sp_inenergy,
#             self.mdot_liquid,
#             pu_pd_from_t = self.liquid_state.lookup('d(U)/d(D)|T'),
#             drho_dt=self.liquid_rhodot
#         )


#         # Eq 32
#         self.pressure_balance_vapor = zilliac.half_eq_32(
#             pP_pT_from_rho = self.vapor_state.lookup('d(P)/d(T)|D'),
#             dTdt = self.vapor_tdot,
#             pP_prho_from_T = self.vapor_state.lookup('d(P)/d(D)|T'),
#             drho_dt=self.vapor_rhodot
#         )
#         self.pressure_balance_liquid = zilliac.half_eq_32(
#             pP_pT_from_rho = self.liquid_state.lookup('d(P)/d(T)|D'),
#             dTdt = self.liquid_tdot,
#             pP_prho_from_T = self.liquid_state.lookup('d(P)/d(D)|T'),
#             drho_dt=self.liquid_rhodot
#         )

#         return self.pressure_balance_vapor - self.pressure_balance_liquid

#     pressure_balance_root = root_scalar(
#         pressure_balance,
#         method = 'secant',
#         maxiter=1000,
#         x0 = self.mdot_liquid / self.liquid_state.density,
#         bracket=[0, 5 * self.mdot_liquid / self.liquid_state.density]
#     )

#     if not pressure_balance_root.converged:
#         if not suppress_warning:
#             raise ValueError(f"ROOT ERROR| {pressure_balance_root}")

#     vdot = pressure_balance_root.root

#     # Update local vars again (may not need to do this)
#     pressure_balance(vdot)

#     # Integrate state
#     self.vapor_mass = np_rk4([self.mdot_vapor, self.vapor_mass], dt)
#     self.liquid_mass = np_rk4([self.mdot_vapor, self.liquid_mass], dt)
#     new_vapor_temp = np_rk4([self.vapor_tdot, self.vapor_state.temp], dt)
#     new_liquid_temp = np_rk4([self.liquid_tdot, self.liquid_state.temp], dt)
#     # new_vapor_density = np_rk4([self.vapor_rhodot, self.vapor_state.density], dt)
#     # new_liquid_density = np_rk4([self.liquid_rhodot, self.liquid_state], dt)

#     print(pretty_dict(self.dict()))

#     # FUCKING ROOT SOLVE FOR PRESURE???? IS THAT 3 ROOT SOLVES???
#     def volume_balance(pressure: float):
#         vapor_volume = self.vapor_mass / PropsSI('D', 'T', new_vapor_temp, 'P', pressure, self.fluid)
#         liquid_volume = self.liquid_mass / PropsSI('D', 'T', new_liquid_temp, 'P', pressure, self.fluid)

#         return self.volume - (vapor_volume + liquid_volume)

#     volume_balance_root = root_scalar(
#         volume_balance,
#         method = 'secant',
#         maxiter=1000,
#         x0 = self.pressure,
#         bracket=[MIN_RESONABLE_PRESSURE_PA, 3 * self.pressure]
#     )

#     if not volume_balance_root.converged:
#         if not suppress_warning:
#             raise ValueError(f"ROOT ERROR| {volume_balance_root}")

#     new_pressure = volume_balance_root.root

#     self.vapor_state.update_from_pt(new_pressure, new_vapor_temp)
#     self.liquid_state.update_from_pt(new_pressure, new_liquid_temp)
