from __future__ import annotations

import os

import numpy as np
import plotly.graph_objects as go
from rocketcea.cea_obj_w_units import CEA_Obj

from ..units import (
    R_JPDEGK_MOL, 
    STD_ATM_PA, 
    convert, 
    imperial_dictionary, 
)
from ..geometry import circle_diameter_from_area
from ..pretty_print import pretty_dict

from ..data_helper import DataStorage
from . import sutton_equations as sutton
from .rocket_geometry import RocketEngineGeometry

# Propellants: https://rocketcea.readthedocs.io/en/latest/propellants.html#propellants-link

# Functions: https://rocketcea.readthedocs.io/en/latest/functions.html


def CEA_SI(ox, fuel):
    if fuel == "IPA":
        fuel = "Isopropanol"
    return CEA_Obj(
        oxName=ox,
        fuelName=fuel,
        useFastLookup=0,
        makeOutput=0,
        isp_units="sec",
        cstar_units="m/sec",
        pressure_units="Pa",
        temperature_units="degK",
        sonic_velocity_units="m/sec",
        enthalpy_units="J/kg",
        density_units="kg/m^3",
        specific_heat_units="J/kg degK",
        viscosity_units="millipoise",
        thermal_cond_units="mcal/cm-K-s",
        fac_CR=None,
        make_debug_prints=False,
    )


class RocketEngineCEA:
    def __init__(
        self,
        ox: str,
        fuel: str,
        chamber_pressure: float,
        mdot: float,
        MR=1.0,
        eps=40.0,
        frozen=0.0,
        frozen_throat=0.0,
        thrust_efficency_fraction=None,
    ):
        self.cea_obj = CEA_SI(ox, fuel)
        self.__chamber_pressure = chamber_pressure
        self.__mdot = mdot
        self.__fuel_mdot = mdot / (MR + 1)
        self.__ox_mdot = mdot - self.__fuel_mdot
        self.__ox = ox
        self.__fuel = fuel
        self.__mix_ratio = MR
        self.__eps = eps
        self.__frozen = frozen
        self.__frozen_throat = frozen_throat

        self.__thrust_eff = thrust_efficency_fraction

        # Use Sutton for throat area, use thraot area for other params
        self.__throat_area = sutton.throat_area(
            self.cstar, self.chamber_pressure, self.mdot
        )
        self.__throat_diameter = circle_diameter_from_area(self.__throat_area)
        self.__exit_area = self.__throat_area * eps
        self.__exit_diameter = circle_diameter_from_area(self.__exit_area)

    def from_fuelmdot(
        ox: str,
        fuel: str,
        chamber_pressure: float,
        fuel_mdot: float,
        MR=1.0,
        eps=40.0,
        frozen=0.0,
        frozen_throat=0.0,
        thrust_efficency_fraction=None,
    ):

        mdot = fuel_mdot * (MR + 1)

        return RocketEngineCEA(
            ox=ox,
            fuel=fuel,
            chamber_pressure=chamber_pressure,
            mdot=mdot,
            MR=MR,
            eps=eps,
            frozen=frozen,
            frozen_throat=frozen_throat,
            thrust_efficency_fraction=thrust_efficency_fraction
        )

    def from_geometry(
        rocket_engine_geometry: RocketEngineGeometry,
        ox: str,
        fuel: str,
        chamber_pressure: float,
        ox_mdot: float,
        fuel_mdot: float,
        frozen=0.0,
        frozen_throat=0.0,
        thrust_efficency_fraction=None
    ):
        return RocketEngineCEA(
            ox=ox,
            fuel=fuel,
            chamber_pressure=chamber_pressure,
            MR=ox_mdot / fuel_mdot,
            mdot=ox_mdot+fuel_mdot,
            eps=rocket_engine_geometry.expansion_ratio,
            frozen=frozen,
            frozen_throat=frozen_throat,
            thrust_efficency_fraction=thrust_efficency_fraction
        )

    @property
    def thrust(self):
        return self.__mdot * self.exit_velocity

    @property
    def thrust_eff(self):
        return self.__thrust_eff

    @property
    def mdot(self):
        return self.__mdot

    @property
    def fuel_mdot(self):
        return self.__fuel_mdot

    @property
    def ox_mdot(self):
        return self.__ox_mdot

    @property
    def throat_diameter(self):
        return self.__throat_diameter

    @property
    def throat_area(self):
        return self.__throat_area

    @property
    def exit_diameter(self):
        return self.__exit_diameter

    @property
    def exit_area(self):
        return self.__exit_area

    @property
    def ox(self):
        return self.__ox

    @property
    def fuel(self):
        return self.__fuel

    @property
    def isp(self):
        return self.cea_obj.get_Isp(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )

    @property
    def cstar(self):
        return self.cea_obj.get_Cstar(self.__chamber_pressure, self.__mix_ratio)

    @property
    def cstar_eff(self):
        return self.__cstar_eff

    @property
    def chamber_pressure(self):
        return self.__chamber_pressure

    @property
    def chamber_temp(self):
        return self.cea_obj.get_Temperatures(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[0]

    @property
    def throat_temp(self):
        return self.cea_obj.get_Temperatures(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[1]

    @property
    def exit_temp(self):
        return self.cea_obj.get_Temperatures(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[2]

    @property
    def chamber_density(self):
        return self.cea_obj.get_Densities(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[0]

    @property
    def throat_density(self):
        return self.cea_obj.get_Densities(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[1]

    @property
    def exit_density(self):
        return self.cea_obj.get_Densities(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[2]

    @property
    def chamber_sp_enthalpy(self):
        return self.cea_obj.get_Enthalpies(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[0]

    @property
    def throat_sp_enthalpy(self):
        return self.cea_obj.get_Enthalpies(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[1]

    @property
    def exit_sp_enthalpy(self):
        return self.cea_obj.get_Enthalpies(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[2]

    @property
    def chamber_exit_pratio(self):
        return self.cea_obj.get_PcOvPe(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )

    @property
    def exit_pressure(self):
        return self.__chamber_pressure / self.chamber_exit_pratio

    @property
    def chamber_thermal_conductivity(self):
        return convert(
            self.cea_obj.get_Chamber_Transport(
                self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen
            )[2],
            "mcal/(cm*degK*s)",
            "watt/(m*degK)",
        )

    @property
    def throat_thermal_conductivity(self):
        return convert(
            self.cea_obj.get_Throat_Transport(
                self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen
            )[2],
            "mcal/(cm*degK*s)",
            "watt/(m*degK)",
        )

    @property
    def exit_thermal_conductivity(self):
        return convert(
            self.cea_obj.get_Exit_Transport(
                self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen
            )[2],
            "mcal/(cm*degK*s)",
            "watt/(m*degK)",
        )

    @property
    def chamber_molecular_weight(self):
        return (
            self.cea_obj.get_Chamber_MolWt_gamma(
                self.__chamber_pressure, self.__mix_ratio, self.__eps
            )[0]
            / 1000
        )

    @property
    def throat_molecular_weight(self):
        return (
            self.cea_obj.get_Throat_MolWt_gamma(
                self.__chamber_pressure, self.__mix_ratio, self.__eps
            )[0]
            / 1000
        )

    @property
    def exit_molecular_weight(self):
        return (
            self.cea_obj.get_exit_MolWt_gamma(
                self.__chamber_pressure, self.__mix_ratio, self.__eps
            )[0]
            / 1000
        )

    @property
    def chamber_sp_R(self):
        return R_JPDEGK_MOL / self.chamber_molecular_weight

    @property
    def throat_sp_R(self):
        return R_JPDEGK_MOL / self.chamber_molecular_weight

    @property
    def exit_sp_R(self):
        return R_JPDEGK_MOL / self.exit_molecular_weight

    @property
    def chamber_gamma(self):
        return self.cea_obj.get_Chamber_MolWt_gamma(
            self.__chamber_pressure, self.__mix_ratio, self.__eps
        )[1]

    @property
    def throat_gamma(self):
        return self.cea_obj.get_Throat_MolWt_gamma(
            self.__chamber_pressure, self.__mix_ratio, self.__eps
        )[1]

    @property
    def exit_gamma(self):
        return self.cea_obj.get_exit_MolWt_gamma(
            self.__chamber_pressure, self.__mix_ratio, self.__eps
        )[1]

    @property
    def throat_to_exit_velocity(self):
        return np.sqrt(2 * (self.throat_sp_enthalpy - self.exit_sp_enthalpy))

    @property
    def chamber_to_exit_velocity(self):
        return np.sqrt(2 * (self.chamber_sp_enthalpy - self.exit_sp_enthalpy))

    @property
    def exit_mach(self):
        return self.cea_obj.get_MachNumber(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )

    @property
    def chamber_sos(self):
        return self.cea_obj.get_SonicVelocities(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[0]

    @property
    def throat_sos(self):
        return self.cea_obj.get_SonicVelocities(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[1]

    @property
    def exit_sos(self):
        return self.cea_obj.get_SonicVelocities(
            self.__chamber_pressure,
            self.__mix_ratio,
            self.__eps,
            self.__frozen,
            self.__frozen_throat,
        )[2]

    @property
    def throat_velocity(self):
        return self.throat_sos

    @property
    def exit_velocity(self):
        return self.exit_mach * self.exit_sos

    @property
    def mix_ratio(self):
        return self.__mix_ratio

    def pressure_study(self, start_pressure: float, end_pressure: float, name=""):

        # Use the data storage to create some easy recorind... dx is limtiing lol
        data: DataStorage = DataStorage.from_linspace(
            start_pressure,
            end_pressure,
            100,
            data_key="Chamber Pressure [Pa]",
            name=name,
        )
        for pressure in data.data_array:
            cea = RocketEngineCEA(
                ox=self.ox,
                fuel=self.fuel,
                chamber_pressure=pressure,
                mdot=self.__mdot,
                MR=self.__mix_ratio,
                eps=self.__eps,
                frozen=self.__frozen,
                frozen_throat=self.__frozen_throat,
            )
            data.record("Atmospheric Pressure [Pa]", STD_ATM_PA)
            record_rocketchamber_data(cea, data)
            data.next_cycle()

        return data.datadict

    def mix_study(self, start_mix_ratio_ratio=0.1, end_mix_ratio_ratio=5, name=""):
        data: DataStorage = DataStorage.from_linspace(
            start=start_mix_ratio_ratio,
            end=end_mix_ratio_ratio,
            increments=500,
            data_key="Mix Ratio [-]",
            name=name,
        )
        for mr in data.data_array:
            cea = RocketEngineCEA(
                ox=self.ox,
                fuel=self.fuel,
                chamber_pressure=self.__chamber_pressure,
                mdot=self.__mdot,
                MR=mr,
                eps=self.__eps,
                frozen=self.__frozen,
                frozen_throat=self.__frozen_throat,
            )
            data.record("Atmospheric Pressure [Pa]", STD_ATM_PA)
            record_rocketchamber_data(cea, data)
            data.next_cycle()

        return data.datadict

    def eps_study(self, start_eps=1.1, end_eps=60, name=""):
        data: DataStorage = DataStorage.from_linspace(
            start=start_eps,
            end=end_eps,
            increments=500,
            data_key="Area Expansion Ratio [-]",
            name=name,
        )
        for eps in data.data_array:
            cea = RocketEngineCEA(
                ox=self.ox,
                fuel=self.fuel,
                chamber_pressure=self.__chamber_pressure,
                mdot=self.__mdot,
                MR=self.__mix_ratio,
                eps=eps,
                frozen=self.__frozen,
                frozen_throat=self.__frozen_throat,
            )
            data.record("Atmospheric Pressure [Pa]", STD_ATM_PA)
            record_rocketchamber_data(cea, data)
            data.next_cycle()

        return data.datadict

    def mdot_study(self, start_mdot=0.1, end_mdot=10, name=""):
        data: DataStorage = DataStorage.from_linspace(
            start=start_mdot,
            end=end_mdot,
            increments=500,
            data_key="mdot [kg/s]",
            name=name,
        )
        for mdot in data.data_array:
            cea = RocketEngineCEA(
                ox=self.ox,
                fuel=self.fuel,
                chamber_pressure=self.__chamber_pressure,
                mdot=mdot,
                MR=self.__mix_ratio,
                eps=self.__eps,
                frozen=self.__frozen,
                frozen_throat=self.__frozen_throat,
            )
            data.record("Atmospheric Pressure [Pa]", STD_ATM_PA)
            record_rocketchamber_data(cea, data)
            data.next_cycle()

        return data.datadict

    def pressure_mix_contour(
        self,
        parameter: str | list,
        start_pressure,
        end_pressure,
        start_mix_ratio=0.1,
        end_mix_ratio=3,
        show_plot=True,
        export_path=None,
    ):

        pressure = np.linspace(start_pressure, end_pressure, 30)
        mix = np.linspace(start_mix_ratio, end_mix_ratio, 30)

        if not isinstance(parameter, list):
            parameter = [parameter]

        for parm in parameter:

            row = []
            for m in mix:
                col = []
                for p in pressure:
                    cea = RocketEngineCEA(
                        ox=self.__ox,
                        fuel=self.__fuel,
                        chamber_pressure=p,
                        MR=m,
                        mdot=self.__mdot,
                        eps=self.__eps,
                        frozen=self.__frozen,
                        frozen_throat=self.__frozen_throat,
                    )
                    col.append(getattr(cea, parm))
                row.append(col)

            fig = go.Figure()
            fig.add_trace(go.Surface(z=np.array(row), x=pressure, y=mix))

            fig.update_layout(
                title=f"|{self.fuel} and {self.ox}|",
                scene=dict(
                    xaxis_title="Chamber Pressure [Pa]",
                    yaxis_title="Mix Ratio [-]",
                    zaxis_title=parm,
                ),
            )

            if export_path is not None:
                fig.write_html(f"{export_path}pressure_mix_{parm}.html")

            if show_plot:
                fig.show()

    def pressure_eps_contour(
        self,
        parameter: str | list,
        start_pressure,
        end_pressure,
        start_eps=1.1,
        end_eps=40,
        show_plot=True,
        export_path=None,
    ):

        pressure = np.linspace(start_pressure, end_pressure, 30)
        eps = np.linspace(start_eps, end_eps, 30)

        if not isinstance(parameter, list):
            parameter = [parameter]

        for parm in parameter:

            row = []
            for e in eps:
                col = []
                for p in pressure:
                    cea = RocketEngineCEA(
                        ox=self.__ox,
                        fuel=self.__fuel,
                        chamber_pressure=p,
                        MR=self.__mix_ratio,
                        mdot=self.__mdot,
                        eps=e,
                        frozen=self.__frozen,
                        frozen_throat=self.__frozen_throat,
                    )
                    col.append(getattr(cea, parm))
                row.append(col)

            fig = go.Figure()
            fig.add_trace(go.Surface(z=np.array(row), x=pressure, y=eps))

            fig.update_layout(
                title=f"|{self.fuel} and {self.ox}|",
                scene=dict(
                    xaxis_title="Chamber Pressure [Pa]",
                    yaxis_title="Area Expansion Ratio [-]",
                    zaxis_title=parm,
                ),
            )

            if export_path is not None:
                fig.write_html(f"{export_path}pressure_eps_{parm}.html")

            if show_plot:
                fig.show()

    @property
    def dict(self):
        dict = {
            "Chamber Density [kg/m^3]": self.chamber_density,
            "Chamber Exit Pressure Ratio [-]": self.chamber_exit_pratio,
            "Chamber Gamma [-]": self.chamber_gamma,
            "Chamber Molecular Weight [kg/mol]": self.chamber_molecular_weight,
            "Chamber Pressure [Pa]": self.chamber_pressure,
            "Chamber Specific Enthalpy [J/kg]": self.chamber_sp_enthalpy,
            "Chamber Specific Gas Constant [J/(kg * degK)]": self.chamber_sp_R,
            "Chamber Specific Gas Constant [J/(kg * degK)]": self.exit_sp_R,
            "Chamber Speed of Sound [m/s]": self.chamber_sos,
            "Chamber Temp [degK]": self.chamber_temp,
            "Chamber Thermal Conductivity [watt/(m*degK)]": self.chamber_thermal_conductivity,
            "Chamber to Exit Velocity [m/s]": self.chamber_to_exit_velocity,
            "Cstar [m/s]": self.cstar,
            "Exit Area [m^2]": self.exit_area,
            "Exit Density [kg/m^3]": self.exit_density,
            "Exit Diameter [m]": self.exit_diameter,
            "Exit Gamma [-]": self.exit_gamma,
            "Exit Mach [-]": self.exit_mach,
            "Exit Molecular Weight [kg/mol]": self.exit_molecular_weight,
            "Exit Pressure [Pa]": self.exit_pressure,
            "Exit Specific Enthalpy [J/kg]": self.exit_sp_enthalpy,
            "Exit Speed of Sound [m/s]": self.exit_sos,
            "Exit Temp [degK]": self.exit_temp,
            "Exit Thermal Conductivity [watt/(m*degK)]": self.exit_thermal_conductivity,
            "Exit Velocity [m/s]": self.exit_velocity,
            "Fuel mdot [kg/s]": self.fuel_mdot,
            "Isp Vac [s]": self.isp,
            "Mixture Ratio [-]": self.mix_ratio,
            "Ox mdot [kg/s]": self.ox_mdot,
            "Throat Area [m^2]": self.throat_area,
            "Throat Density [kg/m^3]": self.throat_density,
            "Throat Diameter [m]": self.throat_diameter,
            "Throat Gamma [-]": self.throat_gamma,
            "Throat Molecular Weight [kg/mol]": self.throat_molecular_weight,
            "Throat Specific Enthalpy [J/kg]": self.throat_sp_enthalpy,
            "Throat Specific Gas Constant [J/(kg * degK)]": self.throat_sp_R,
            "Throat Speed of Sound [m/s]": self.throat_sos,
            "Throat Temp [degK]": self.throat_temp,
            "Throat Thermal Conductivity [watt/(m*degK)]": self.throat_thermal_conductivity,
            "Throat Velocity [m/s]": self.throat_velocity,
            "Throat to Exit Velocity [m/s]": self.throat_to_exit_velocity,
            "Thrust Ideal [N]": self.thrust,
            "Mdot [kg/s]": self.mdot,
        }

        # Add in optional parameters
        if self.thrust_eff is not None:
            dict = dict | {
                "Thrust Efficency Fraction [-]": self.thrust_eff,
                "Thrust With Losses [N]": self.thrust * self.thrust_eff,
            }

            unsorted = list(dict.keys())
            unsorted.sort()
            dict = {i: dict[i] for i in unsorted}
        
        return dict

    def string(self, round_places=3):
        return pretty_dict(self.dict, round_places=round_places)

    @property
    def imperial_dict(self):
        return imperial_dictionary(self.dict)

    def imperial_string(self, round_places=3):
        return pretty_dict(self.imperial_dict, round_places)


def record_rocketchamber_data(cea: RocketEngineCEA, data: DataStorage):
    for key, value in cea.dict.items():
        data.record(key, value)
    data.record(
        "Sutton Velocity [m/s]",
        sutton.exit_velocity(
            gamma=cea.chamber_gamma,
            sp_R=cea.chamber_sp_R,
            chamber_pressure=cea.chamber_pressure,
            combustion_temp=cea.chamber_temp,
            exit_pressure=cea.exit_pressure,
        ),
    )
