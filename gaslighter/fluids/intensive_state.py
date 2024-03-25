from __future__ import annotations
import sys

from CoolProp.CoolProp import PropsSI

from ..errors import check_float, check_str

def look_from_quality(
    target: str | list,
    prop: str,
    value: float,
    quality: float,
    fluid: str
):
    return PropsSI(target, prop, value, 'Q', quality, fluid)

class IntensiveState:
    def __init__(
        self, prop_1: str, value_1: float, prop_2: str, value_2: float, fluid: str
    ):
        check_str(prop_1)
        check_str(prop_2)
        check_float(value_1)
        check_float(value_2)
        check_str(fluid)
        self.__prop_1 = prop_1
        self.__value_1 = value_1
        self.__prop_2 = prop_2
        self.__value_2 = value_2
        self.__fluid = fluid
        self.__update_state()

    def from_pt(pressure: float, temperature: float, fluid: str):
        check_float(pressure)
        check_float(temperature)
        return IntensiveState("P", pressure, "T", temperature, fluid)

    def __update_state(self):
        # Lookup common properties
        self.__pressure = self.lookup("P")
        self.__temp = self.lookup("T")
        self.__density = self.lookup("D")
        self.__molar_mass = self.lookup("MOLAR_MASS")
        self.__sp_inenergy = self.lookup("UMASS")
        self.__sp_enthalpy = self.lookup("HMASS")
        self.__sp_entropy = self.lookup("SMASS")
        self.__cp = self.lookup("CPMASS")
        self.__cv = self.lookup("CVMASS")
        self.__gamma = self.lookup("ISENTROPIC_EXPANSION_COEFFICIENT")

    @property
    def pressure(self):
        return self.__pressure

    @property
    def temp(self):
        return self.__temp

    @property
    def density(self):
        return self.__density

    @property
    def molar_mass(self):
        return self.__molar_mass

    @property
    def sp_inenergy(self):
        return self.__sp_inenergy

    @property
    def sp_enthalpy(self):
        return self.__sp_enthalpy

    @property
    def sp_entropy(self):
        return self.__sp_entropy

    @property
    def cp(self):
        return self.__cp

    @property
    def cv(self):
        return self.__cv

    @property
    def gamma(self):
        return self.__gamma


    @property
    def fluid(self):
        return self.__fluid

    def lookup(self, prop: str) -> float:
        """Lookup a property from the current state"""
        check_str(prop)

        if prop == self.__prop_1:
            return self.__value_1

        if prop == self.__prop_2:
            return self.__value_2

        try:
            return PropsSI(
                prop,
                self.__prop_1,
                self.__value_1,
                self.__prop_2,
                self.__value_2,
                self.__fluid,
            )
        except:
            raise ValueError(
                f"ERROR| Props Lookup error with ({prop},{self.__prop_1},{self.__value_1},{self.__prop_2},{self.__value_2})"
            )

    def trivial(self, prop: str) -> float:
        check_str(prop)

        if prop == self.__prop_1:
            return self.__value_1

        if prop == self.__prop_2:
            return self.__value_2

        try:
            return ProcessLookupError(
                prop,
                self.fluid
            )
        except:
            raise ValueError(
                f"ERROR| Props Trivial Lookup error with ({prop}, {self.fluid})"
            )

    def update_from_props(self, prop_1: str, value_1: str, prop_2: str, value_2: str):
        check_str(prop_1)
        check_str(prop_2)
        check_float(value_1)
        check_float(value_2)
        self.__prop_1 = prop_1
        self.__value_1 = value_1
        self.__prop_2 = prop_2
        self.__value_2 = value_2
        self.__update_state()

    def update_from_du(self, density: float, sp_inenergy: float):
        check_float(density)
        check_float(sp_inenergy)
        self.__prop_1 = "D"
        self.__value_1 = density
        self.__prop_2 = "UMASS"
        self.__value_2 = sp_inenergy
        self.__update_state()

    def update_from_pt(self, pressure: float, temperature: float):
        check_float(pressure)
        check_float(temperature)
        self.__prop_1 = "P"
        self.__value_1 = pressure
        self.__prop_2 = "T"
        self.__value_2 = temperature
        self.__update_state()

    def isentropic(self, prop: str, value: float):
        """Returns a new state under istentropic conditions"""
        check_str(prop)
        check_float(value)

        return IntensiveState(prop, value, "SMASS", self.__sp_entropy, self.__fluid)

    def isothermal(self, prop: str, value: float):
        """Returns a new state under isothermal conditions"""
        check_str(prop)
        check_float(value)

        return IntensiveState(prop, value, "T", self.__temp, self.__fluid)

    def isenthalpic(self, prop: str, value: str):
        """Returns a new state under isenthalpic conditions"""
        check_str(prop)
        check_float(value)
        return IntensiveState(prop, value, "HMASS", self.__sp_enthalpy, self.__fluid)
