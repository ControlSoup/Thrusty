from dataclasses import dataclass
from .intensive_state import IntensiveState


# Very bare bones data containter for volume
class BasicStaticVolume():

    def __init__(self, mass: float, volume: float, inenergy: float, fluid):
        self.__mass = mass
        self.__volume = volume
        self.__inenergy = inenergy
        self.state = IntensiveState("D", mass / volume, "UMASS", inenergy / mass, fluid)

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
        state =IntensiveState("P", pressure, "T", temp, fluid)
        mass = state.density * volume
        return BasicStaticVolume(
            mass,
            volume,
            state.sp_inenergy * mass,
            fluid
        )

    def update_mu(self, mass: float, inenergy: float):
        self.__mass = mass
        self.__inenergy = inenergy

        self.state.update_from_du(
            self.mass / self.volume,
            self.inenergy / self.mass
        )




