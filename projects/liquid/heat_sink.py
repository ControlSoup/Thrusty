from gaslighter.heat_transfer import plot_fdm_solution
from gaslighter import PCBWAY_CU_DIFFUSIVITY, STD_ATM_K, convert

# Heat Sink Graph / Model of the engine

# Materials from : https://www.pcbway.com/rapid-prototyping/cnc-machining/metal/copper/Copper-0/

import gaslighter_rust
import numpy as np

intial_temps = list(np.zeros(5))
intial_temps[0] = 100

print(gaslighter_rust.fdm_1d(
    intial_temps,
    1,
    1,
    1
))
