import numpy as np

from gaslighter.heat_transfer import plot_fdm_solution
from gaslighter import STD_ATM_K, convert

# Heat Sink Graph / Model of the engine

# Materials from : https://www.pcbway.com/rapid-prototyping/cnc-machining/metal/copper/Copper-0/

CONVECTION_TEMP_THROAT_K = 1446.17034373
NODES = 250
MAX_THICKNESS_IN = convert(3, 'in', 'm')
MAX_TIME = 5


# Create a polynomial to find average diffusivity of our system
# https://www.researchgate.net/figure/Thermal-diffusivity-of-copper-as-a-functlon-of-temperature_fig1_236269958
copper_high_temp_diffivity = np.poly1d(np.polyfit(
    convert([614.6031746031746,718.7301587301588,843.1746031746032,934.6031746031746,1008.2539682539683], 'degC', 'degK'),
    convert([0.4677551020408163,0.3648979591836734,0.23755102040816323,0.14693877551020407,0.07836734693877556], 'cm^2/s', 'm^2/s'),
    1
))
AVG_DIFFUSIVITY = copper_high_temp_diffivity(np.mean([CONVECTION_TEMP_THROAT_K, STD_ATM_K]))

# NOTE: There is a serious limitation of this fdm solve,
# it does not consider convection, and assumes the outter wall will be ambient... which it won't be
plot_fdm_solution(
    diffusivity = AVG_DIFFUSIVITY,
    start_t = CONVECTION_TEMP_THROAT_K,
    end_t = STD_ATM_K,
    nodes = NODES,
    distance = MAX_THICKNESS_IN,
    max_time = MAX_TIME,
    export_path = "plots/heat_imperial.html",
    imperial_results=True
)
plot_fdm_solution(
    diffusivity = AVG_DIFFUSIVITY,
    start_t = CONVECTION_TEMP_THROAT_K,
    end_t = STD_ATM_K,
    nodes = NODES,
    distance = MAX_THICKNESS_IN,
    max_time = MAX_TIME,
    export_path = "plots/heat_sink.html",
    imperial_results=False
)
