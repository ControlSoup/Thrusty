from CoolProp.Coolprop import PropsSI


class IntensiveState():
    def __init__(
        self,
        prop_1: str, value_1: str,
        prop_2: str, value_2: str,
        fluid: str
    ):
        self.__prop_1 = prop_1
        self.__value_1 = value_1
        self.__prop_2 = prop_2
        self.__value_2 = value_2
        self.__fluid = fluid
        self.__update_state()

    def __update_state(self):
        # Lookup common properties
        self.__pressure = self.lookup("P")
        self.__temp = self.lookup("T")
        self.__sp_inenergy = self.lookup("UMASS")
        self.__sp_enthalpy = self.lookup("HMASS")
        self.__sp_entropy = self.lookup("SMASS")
        self.__cp = self.lookup("CPMASS")
        self.__cv = self.lookup("CVMASS")

    def presure(self):
        return self.__pressure

    def temp(self):
        return self.__temp

    def sp_inenergy(self):
        return self.__sp_inenergy

    def sp_enthalpy(self):
        return self.__sp_enthalpy

    def sp_entropy(self):
        return self.__sp_entropy

    def cp(self):
        return self.__cp

    def cv(self):
        return self.__cv

    def lookup(self, prop: str) -> float:
        ''' Lookup a property from the current state
        '''

        if prop == self.__prop_1:
            return self.__value_1

        if prop == self.__prop_2:
            return self.__value_2

        return PropsSI(
            prop,
            self.__prop_1, self.__value_1,
            self.__prop_2, self.__value_2,
            self.__fluid
        )

    def update_from_props(
        self,
        prop_1: str, value_1: str,
        prop_2: str, value_2: str
    ):
        self.__prop_1 = prop_1
        self.__value_1 = value_1
        self.__prop_2 = prop_2
        self.__value_2 = value_2
        self.__update_state()

    def istentropic(self, prop: str, value: str):
        ''' Returns a new state under istentropic conditions
        '''

        return IntensiveState(
            prop, value,
            'SMASS',self.__sp_entropy
        )

    def isothermal(self, prop: str, value: str):
        ''' Returns a new state under isothermal conditions
        '''

        return IntensiveState(
            prop, value,
            'T', self.__temp
        )

    def isenthalpic(self, prop: str, value: str):
        ''' Returns a new state under isenthalpic conditions
        '''

        return IntensiveState(
            prop, value,
            'HMSAS', self.__sp_enthalpy
        )