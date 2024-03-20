from ..errors import check_float, check_str
from .intensive_state import IntensiveState
from CoolProp.CoolProp import PropsSI


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

class ZillacKarabeyogluVolume:
    def __init__(
        self,
        fill_fraction: float,
        pressure: float,
        volume: float,
        fluid: float
    ):
        '''
        Assumptions:
            - Starts at saturation
            - No heat transfer from the walls

        Source:
            Review and Evaluation of Models for Self-Pressurizing Propellant Tank Dynamics [Jonah E. Zimmerman]
            Uses equations [24, 25, 35]
        '''
        self.__fill_fraction = fill_fraction
        self.__fluid = fluid

        self.__pressure = pressure
        self.__liquid_state = IntensiveState('Q', 0, 'P', pressure, self.__fluid)
        self.__liquid_mass = self.__liquid_state.density * fill_fraction * volume
        self.__liquid_inenergy = self.__liquid_state.sp_inenergy * self.__liquid_mass
        self.__liquid_volume = self.__liquid_mass / self.__liquid_state.density

        self.__vapor_state = IntensiveState('Q', 1, 'P', pressure, self.__fluid)
        self.__vapor_mass = self.__vapor_state.density * (1 - self.__fill_fraction) * volume
        self.__vapor_inenergy = self.__vapor_state.sp_inenergy * self.__vapor_mass
        self.__vapor_volume = self.__vapor_mass / self.__vapor_state.density

        self.__liquid_mdot = 0.0
        self.__vapor_mdot = 0.0
        self.__cond_mdot = 0.0

    @property
    def pressure(self):
        return self.__pressure

    def update_from_liquid_mdot(self, liquid_mdot: float):
        self.__liquid_mdot = liquid_mdot

        # Eq 29
        if self.pressure < self.__vapor_state.vapor_pressure:
            self.__cond_mdot = 0.0
        else:
            self.__cond_mdot = (self.pressure - self.__vapor_state.vapor_pressure) * self.__vapor_volume * self.__vapor_state.molar_mass



