import numpy as np
from dataclasses import dataclass
from .intensive_state import IntensiveState
from ..errors import check_float, check_str


# Very bare bones data containter for volume
class BasicStaticVolume():

    def __init__(self, mass: float, volume: float, inenergy: float, fluid: str):

        check_float(mass)
        check_float(volume)
        check_float(inenergy)
        check_str(fluid)

        self.__mass = mass
        self.__volume = volume
        self.__inenergy = inenergy
        self.state = IntensiveState(
            "D", self.__mass / self.__volume,
            "UMASS", self.__inenergy / self.__mass,
            fluid
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
        return BasicStaticVolume(
            mass,
            volume,
            state.sp_inenergy * mass,
            fluid
        )

    def update_mu(self, mass: float, inenergy: float):

        check_float(mass)
        check_float(inenergy)

        self.__mass = mass
        self.__inenergy = inenergy

        self.state.update_from_du(
            self.__mass / self.__volume,
            self.__inenergy / self.__mass
        )




