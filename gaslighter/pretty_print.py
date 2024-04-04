import numpy as np


def pretty_key_val(key: str, value, round_places: int = 3):

    if isinstance(value, float) or isinstance(value, np.ndarray):
        val = np.round(value, round_places)
    else:
        val = value

    return f"{key} = {val}\n"


def pretty_dict(dict, round_places: int = 3):
    string = ""
    for key in dict:
        string += pretty_key_val(key, dict[key], round_places)
    return string


def sort_dict(dict: dict):
    unsorted = list(dict.keys())
    unsorted.sort()
    new_dict = {i: dict[i] for i in unsorted}
    return new_dict
