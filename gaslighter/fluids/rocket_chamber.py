from __future__ import annotations
import os
import numpy as np
from rocketcea.cea_obj_w_units import CEA_Obj
import plotly.graph_objects as go
from ..runtimes import DataStorage
from CoolProp.CoolProp import PropsSI

# Propellants: https://rocketcea.readthedocs.io/en/latest/propellants.html#propellants-link

# Functions: https://rocketcea.readthedocs.io/en/latest/functions.html

def CEA_SI(ox, fuel):
    if fuel == 'IPA':
        fuel = 'Isopropanol'
    return CEA_Obj(
        oxName=ox, fuelName=fuel,
        useFastLookup=0, makeOutput=0,
        isp_units='sec',
        cstar_units='m/sec',
        pressure_units='Pa',
        temperature_units='degK',
        sonic_velocity_units='m/sec',
        enthalpy_units='J/kg',
        density_units='kg/m^3',
        specific_heat_units='J/kg degK',
        viscosity_units='millipoise',
        thermal_cond_units='mcal/cm-K-s',
        fac_CR=None,
        make_debug_prints=False
    )

class RocketChamber():
    def __init__(
        self,
        ox: str,
        fuel: str,
        chamber_pressure: float,
        MR = 1.0,
        eps = 40.0,
        frozen = 0.0,
        frozen_throat = 0.0
    ):
        self.cea_obj = CEA_SI(ox, fuel)
        self.__chamber_pressure = chamber_pressure
        self.__ox = ox
        self.__fuel = fuel
        self.__mix_ratio = MR
        self.__eps = eps
        self.__frozen = 0.0
        self.__frozen_throat = 0.0

    @property
    def ox(self):
        return self.__ox

    @property
    def fuel(self):
        return self.__fuel

    @property
    def isp(self):
        return self.cea_obj.get_Isp(self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen, self.__frozen_throat)

    @property
    def cstar(self):
        return self.cea_obj.get_Cstar(self.__chamber_pressure, self.__mix_ratio)

    @property
    def chamber_pressure(self):
        return self.__chamber_pressure

    @property
    def chamber_temp(self):
        return self.cea_obj.get_Temperatures(self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen, self.__frozen_throat)[0]

    @property
    def throat_temp(self):
        return self.cea_obj.get_Temperatures(self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen, self.__frozen_throat)[1]

    @property
    def exit_temp(self):
        return self.cea_obj.get_Temperatures(self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen, self.__frozen_throat)[2]

    @property
    def chamber_density(self):
        return self.cea_obj.get_Densities(self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen, self.__frozen_throat)[0]

    @property
    def throat_density(self):
        return self.cea_obj.get_Densities(self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen, self.__frozen_throat)[1]

    @property
    def exit_density(self):
        return self.cea_obj.get_Densities(self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen, self.__frozen_throat)[2]

    @property
    def chamber_sp_enthalpy(self):
        return self.cea_obj.get_Chamber_H(self.__chamber_pressure, self.__mix_ratio, self.__eps)

    @property
    def throat_sp_enthalpy(self):
        return self.cea_obj.get_Enthalpies(self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen, self.__frozen_throat)[1]

    @property
    def exit_sp_enthalpy(self):
        return self.cea_obj.get_Enthalpies(self.__chamber_pressure, self.__mix_ratio, self.__eps, self.__frozen, self.__frozen_throat)[2]

    @property
    def exit_velocity(self):
        return np.sqrt(2 * (self.throat_sp_enthalpy - self.exit_sp_enthalpy))

    @property
    def cf(self):
        return self.cea_obj.get_PambCf(self.__chamber_pressure, self.__mix_ratio, self.__eps)[0]

    @property
    def mix_ratio(self):
        return self.__mix_ratio
    

    def pressure_study(self,start_pressure: float, end_pressure: float, name=""):

        # Use the data storage to create some easy recorind... dt_s is limtiing lol
        data: DataStorage = DataStorage.from_linspace(start_pressure, end_pressure, 100, time_key='Chamber Pressure [Pa]', name=name)
        for pressure in data.time_array_s:
            cea = RocketChamber(self.ox, self.fuel, pressure, self.__mix_ratio, self.__eps, self.__frozen, self.__frozen_throat)
            record_rocketchamber_data(cea, data)
            data.next_cycle()

        return data.datadict

    def mix_study(self, start_mix_ratio_ratio = 0.1, end_mix_ratio_ratio = 5, name=""):
        data: DataStorage = DataStorage.from_linspace(start=start_mix_ratio_ratio, end=end_mix_ratio_ratio, increments=100, time_key='Mix Ratio [-]', name=name)
        for mr in data.time_array_s:
            cea = RocketChamber(self.ox, self.fuel, self.__chamber_pressure, mr, self.__eps, self.__frozen, self.__frozen_throat)
            record_rocketchamber_data(cea, data)
            data.next_cycle()

        return data.datadict

    def pressure_mix_contour(self, parameter: str | list, start_pressure, end_pressure, start_mix_ratio = 0.1, end_mix_ratio = 3, export_path = None):

        pressure =  np.linspace(start_pressure, end_pressure, 10)
        mix = np.linspace(start_mix_ratio, end_mix_ratio, 10)

        if not isinstance(parameter, list):
            parameter = [parameter]

        for parm in parameter:

            row =[]
            for m in mix:
                col = []
                for p in pressure:
                    cea = RocketChamber(self.__ox, self.__fuel, p, m, self.__eps, self.__frozen, self.__frozen_throat)
                    col.append(getattr(cea, parm))
                row.append(col)

            fig = go.Figure()
            fig.add_trace(go.Surface(z = np.array(row), x = pressure, y = mix))

            fig.update_layout(
                title=f"|{self.fuel} and {self.ox}|",
                scene=dict(
                    xaxis_title = "Pressure [Pa]",
                    yaxis_title = "Mix Ratio [-]",
                    zaxis_title = parm
                )
            )

            if export_path is not None:
                fig.write_html(os.path.join(export_path, f"{parm}.html"))
            else:
                fig.show()


def record_rocketchamber_data(cea: RocketChamber, data: DataStorage):
    data.record_data("Isp [s]", cea.isp)
    data.record_data("Cstar [m/s]", cea.cstar)
    data.record_data("Chamber Temp [degK]", cea.chamber_temp)
    data.record_data("Throat Temp [degK]", cea.throat_temp)
    data.record_data("Exit Temp [degK]", cea.exit_temp)
    data.record_data("Chamber Density [kg/m^3]", cea.chamber_density)
    data.record_data("Throat Density [kg/m^3]", cea.throat_density)
    data.record_data("Exit Density [kg/m^3]", cea.exit_density)
    data.record_data("Chamber Specific Enthalpy [J/kg]", cea.chamber_sp_enthalpy)
    data.record_data("Throat Specific Enthalpy [J/kg]", cea.throat_sp_enthalpy)
    data.record_data("Exit Specific Enthalpy [J/gk]", cea.exit_sp_enthalpy)
    data.record_data("Exit Velocity [m/s]", cea.exit_velocity)
    data.record_data("CF [-]", cea.cf)
    data.record_data("Mix Ratio [-]", cea.mix_ratio)


