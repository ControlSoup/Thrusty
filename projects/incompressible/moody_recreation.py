import numpy as np
from tqdm import tqdm

from gaslighter import DataStorage, fluids

data: DataStorage = DataStorage.from_geomspace(
    start=1000, end=10e6, icrements=10000, data_key="Reynolds Number [-]"
)

relative_roughness = np.geomspace(0.05, 0.000002, num=28, endpoint=True)

for Re in tqdm(data.data_array):
    for relrough in relative_roughness:
        ff = fluids.friction_factor(Re, relrough, suppress_warnings=True)
        data.record(f"{relrough} [-]", ff)
    data.next_cycle()

data.plot_all(
    y_axis_tile="Friction Factor [-]",
    export_path="results/moody_diagram.html",
    log_x=True,
)

data: DataStorage = DataStorage.from_geomspace(
    start=4000, end=30000, increments=1000, data_key="Reynolds Number [-]"
)
relative_roughness = np.geomspace(0.05, 0.000002, num=5, endpoint=True)

for Re in tqdm(data.data_array):
    for relrough in relative_roughness:
        ff_colebrook = fluids.friction_factor(Re, relrough, suppress_warnings=True)
        ff_jain = fluids.jain_forumulation(Re, relrough)
        data.record(f"{relrough}_colebrook [-]", ff_colebrook)
        data.record(f"{relrough}_jain [-]", ff_jain)

    data.next_cycle()

data.plot_all(
    y_axis_tile="Friction Factor [-]",
    export_path="results/jain_vs_colebrook_diagram.html",
    log_x=True,
)
