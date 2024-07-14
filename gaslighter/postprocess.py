import numpy as np
from scipy.signal import butter, sosfilt
from copy import deepcopy

# =============================================================================
# Trimming data
# =============================================================================

def first_index_greater(array: np.array, value: float):
    try:
        return np.where(array >= value)[0][0]
    except Exception as e:
        raise ValueError(f"ERROR| first_index_greater failed with {e}")

def last_index_greater(array: np.array, value: float):
    try:
        np.where(array >= value)[-1][0]
    except Exception as e:
        raise ValueError(f"ERROR| last_index_greater failed with {e}")

def first_index_less(array: np.array, value: float):
    try:
        return np.where(array >= value)[0][0]
    except Exception as e:
        raise ValueError(f"ERROR| first_index_less failed with {e}")

def last_index_less(array: np.array, value: float):
    try:
        return np.where(array >= value)[-1][0]
    except Exception as e:
        raise ValueError(f"ERROR| first_index_less failed with {e}")

def diff_with_first_index(array: np.array):
    new_array = np.zeros_like(array)
    new_array[1:] = np.diff(array)
    return new_array

def time_align_datadict(datadict: dict, time_key: str, t_0_index: float) -> None:
    new_datadict = deepcopy(datadict)
    new_datadict = new_datadict - datadict[time_key][t_0_index]
    return new_datadict

def trim_datadict(datadict: dict, start_index: int, end_index: int):
    new_datadict = deepcopy(datadict)
    for key, data in new_datadict.items():
        new_datadict[key] = data[start_index: end_index + 1]
    return new_datadict

def trim_time_datadict(datadict: dict, x_key: str, start_time: float, end_time: float = None):
    if end_time:
        return trim_datadict(datadict, first_index_greater(datadict[x_key], start_time), len(datadict[x_key]) - 1)

    return trim_datadict(datadict, first_index_greater(datadict[x_key], start_time), first_index_greater(datadict[x_key], end_time))

# =============================================================================
# Simple constant dt assumptions
# =============================================================================

def moving_average(array: np.array, window: float, freq: float):
    ''' Source: https://stackoverflow.com/questions/14313510/how-to-calculate-rolling-moving-average-using-python-numpy-scipy
    '''

    index = int(freq / window)
    cumsum = np.cumsum(array)
    cumsum[index:] = cumsum[index:] - cumsum[:-index]

    return cumsum[index - 1:] / index

def scipy_butter(
    array: np.array,
    order: int,
    cutoff_freq: float,
    sys_freq: float,
    btype: str = 'lowpass',
    analog: bool = False
):
    sos = butter(
        N = order,
        Wn = cutoff_freq,
        btype = btype,
        analog = analog,
        output='sos',
        fs=sys_freq
    )
    return sosfilt(sos, array)

def integral(array: np.array, freq):
    ''' Very simple cumunlative integral
    '''
    return np.cumsum(array) / freq

def derivative(array: np.array, freq):
    ''' Very simple and slow computed derivative
    '''
    derivative = np.zeros_like(array)
    for i,val in enumerate(array):
        if i > 0:
            derivative[i] = freq / (array[i] - array[i - 1])




