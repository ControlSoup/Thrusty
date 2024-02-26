import numpy as np
from tqdm import tqdm

from gaslighter import DataStorage, fluids

data: DataStorage = DataStorage.from_geomspace(
    2000, 5000, 10000, time_key="Reynolds Number [-]"
)

relative_roughness = np.geomspace(0.05, 0.000002, num=28, endpoint=True)

for Re in tqdm(data.time_array_s):
    for relrough in relative_roughness:
        ff = fluids.friction_factor(Re, relrough, suppress_warning=True)
        data.record_data(f"{relrough} [-]", ff)
    data.next_cycle()

data.plot_all(
    y_axis_tile="Friction Factor [-]",
    export_path="results/moody_transition_diagram.html",
    log_x=True,
)
