import numpy as np

def check_float(var):
    if(
        not isinstance(var, int)
        and not isinstance(var, float)
    ):
        raise ValueError(f"ERROR| [{var}] must be of type float or int")

def check_str(var):
    if not isinstance(var, str):
        raise ValueError(f"ERROR| [{var}] must be of type str")