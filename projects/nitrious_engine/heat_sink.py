import numpy as np

from gaslighter import STD_ATM_K, convert
from gaslighter.heat_transfer import plot_fdm_solution

# Heat Sink Graph / Model of the engine

CONVECTION_TEMP_THROAT_K = convert(1781, 'degF', 'degK')
NODES = 150
MAX_THICKNESS_IN = convert(1.25,"in", "m")
MAX_TIME = 5

# Copper C360 diffusivity is ~ 3.28e-5 + (7.88e-9 * T)
# file:///home/bohdi/Downloads/Livre_Rappaz_Symposium_2016.pdf
AVG_DIFFUSIVITY = 3.91e-5

plot_fdm_solution(
    diffusivity=AVG_DIFFUSIVITY,
    start_t=CONVECTION_TEMP_THROAT_K,
    end_t=STD_ATM_K,
    nodes=NODES,
    distance=MAX_THICKNESS_IN,
    max_time=MAX_TIME,
    export_path="plots/heat_imperial.html",
    imperial_results=True,
)
plot_fdm_solution(
    diffusivity=AVG_DIFFUSIVITY,
    start_t=CONVECTION_TEMP_THROAT_K,
    end_t=STD_ATM_K,
    nodes=NODES,
    distance=MAX_THICKNESS_IN,
    max_time=MAX_TIME,
    export_path="plots/heat_sink.html",
    imperial_results=False,
)
