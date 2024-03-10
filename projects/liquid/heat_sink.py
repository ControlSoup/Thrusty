
# Heat Sink Graph / Model of the engine
# Materials from : https://www.pcbway.com/rapid-prototyping/cnc-machining/metal/copper/Copper-0/

import gaslighter_rust
from gaslighter import PCBWAY_CU_DIFFUSIVITY, STD_ATM_K, convert
import numpy as np
import plotly.graph_objects as go

"""
I don't love this scrapy glueing of rust and python,
but I don't want to spend lots of time making nice looking iterfaces
"""

def plot_results(results: list):
    d = np.zeros_like(results[:][-1])
    for i, dx in enumerate(results[:][-1]):

        if i == 0:
            continue

        d[i] = d[i - 1] + dx


    time = results[:][-2]
    temp_history = results[:][0:-1]

    # Create initial plot
    fig = go.Figure()

    # Add initial trace (only the first temperature vs distance graph)
    fig.add_trace(go.Heatmap(z=temp_history[0], y=[time[0]] * len(d), x=d, colorscale='Viridis'))

    # Add scrollbar
    fig.update_layout(
        title="Temperature vs Distance",
        xaxis_title="Distance [m]",
        yaxis_title="Time [s]",
        sliders=[{
            "active": 0,
            "steps": [{"label": f"Time: {t}", "method": "update", "args": [{"z": [temp_history[i]]}, {"title": f"Temperature vs Distance - Time: {t}"}]} for i, t in enumerate(time)],
            "pad": {"t": 50},
            "currentvalue": {"visible": True, "prefix": "Time: "},
            "transition": {"duration": 300, "easing": "cubic-in-out"}
        }]
    )

    fig.show()

intial_temps = list(np.zeros(100))
intial_temps[0] = 100

results = gaslighter_rust.fdm_1d(
    intial_temps,
    0.001,
    1,
    1
)

plot_results(results)


