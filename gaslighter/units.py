from __future__ import annotations
import re
from pint import UnitRegistry
import numpy as np
# ------------------------------------------------------------------------------
# Unit Conversion wrapper
# ------------------------------------------------------------------------------

# Source:https://en.wikipedia.org/wiki/Standard_temperature_and_pressure
STD_G_MPS2 = 9.80665
STD_ATM_PA = 101_325
STD_ATM_K = 288.15
FP_ORIFICE_CD = 0.65
R_JPDEGK_MOL = 8.31446261815324

ureg = UnitRegistry()
ureg.define('psia = psi')
ureg.define('psid = psi')
ureg.define('lbm = lb')
ureg.define(f'Cv = Cda / 38')
ureg.define(f'Cda_in2 = in^2')
ureg.define(f'Cda_m2 = m^2')

def convert(value: float, in_units: str, out_units: str):
    '''
    Converts a unit from in_units to out_units
    Compatible Strings: https://github.com/hgrecco/pint/blob/master/pint/default_en.txt
    '''
    if in_units == out_units:
        return value

    _u = ureg.Quantity(
        value,
        in_units
    )

    return _u.to(out_units).magnitude


def convert_many(*convert_tuple):
    '''
    Converts many units in the convert() function form
    '''
    out_list = []
    for tuple in convert_tuple:
        out_list.append(
            convert(tuple[0],tuple[1],tuple[2])
        )

    return out_list if len(out_list) > 0 else out_list[0]

def get_brack_units(string: str):
    '''
    Returns the units inside the first []
    '''
    return re.findall(r'\[(.*?)\]', string)[0]

def string_to_imperial(string: str):


    def replace(match):

        string =  match.group(0)
        if string == "[watt/(m*degK)]":
            return string.replace('watt/(m*degK)',"Btu/(hr*ft*degF)")

        if 'm' in string:
            string = re.sub(r'\bm\b', 'in', string)

        if 'kg' in string:
            string = string.replace('kg', 'lbm')

        if 'N' in string:
            string = string.replace('N', 'lbf')

        if 'J' in string:
            string = string.replace('J', 'ft*lbf')

        if 'degK' in string:
            string = string.replace('degK', 'degF')

        if 'Pa' in string:
            string = string.replace('Pa', 'psia')

        if 'watt' in string:
            string = string.replace('watt','ft*lbf/s')

        return string

    # Replace the text within brackets based on different conditions
    return re.sub(r'\[.*?\]', replace, string)

def imperial_dictionary(dictionary: dict[str, np.array]):
    imperial = {}

    for key, value in dictionary.items():
        new_key = string_to_imperial(key)
        current_units = get_brack_units(key)

        new_units = get_brack_units(new_key)
        try:
            imperial[new_key] = convert(value, current_units, new_units)
        except:
            raise ValueError(f" CANT CONVERT: {value}, {current_units} to {new_units}")

    return imperial