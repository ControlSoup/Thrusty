import numpy as np

def np_derivative(array: np.array):
    new_array = np.roll(array, 1)
    new_array[0] = 0.0
    return new_array

def np_rk4(states: np.array, dt: float):

    if not isinstance(states, np.ndarray):
        states = np.array(states)

    k1 = np_derivative(states)
    k2 = np_derivative(states + (k1 * dt / 2.0))
    k3 = np_derivative(states + (k2 * dt / 2.0))
    k4 = np_derivative(states + k3 * dt)

    integrate = states + ((k1 + (k2 * 2.0) + (k3 * 2.0) + k4) * dt / 6.0)

    # Chop off the first element as its deriviative is always 0.0
    new_values = integrate[1:]

    if len(new_values) > 1:
        return new_values
    else:
        return new_values[0]

