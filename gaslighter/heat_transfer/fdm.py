import plotly.graph_objects as go
import numpy as np
from tqdm import tqdm
from ..integration import np_rk4
from ..units import convert

"""
Source: https://www-udc.ig.utexas.edu/external/becker/teaching/557/problem_sets/problem_set_fd_explicit.pdf
"""

def fdm_dT_dt(
    diffusivity: float,
    next_node_t: float,
    current_node_t: float,
    last_node_t: float,
    dx: float
):

    """Discreteized 1D Heat equation"""
    heat_comp = (next_node_t - (2 * current_node_t) + last_node_t)

    return diffusivity * heat_comp / dx**2

def fdm_newT_explicit(
    diffusivity: float,
    next_node_t: float,
    current_node_t: float,
    last_node_t: float,
    dx: float,
    dt: float
):
    """Explicit 1D FDM Heat equation"""

    heat_comp = (next_node_t - (2 * current_node_t) + last_node_t)

    return current_node_t +  (diffusivity * dt)  * (heat_comp / dx**2)


def plot_fdm_solution(
    diffusivity: float,
    start_t: float,
    end_t: float,
    nodes: int,
    distance: float,
    max_time: float,
    method = "rk4",
    dt: float = None,
    export_path = None,
    imperial_results = True
):
    """1D Heat Transfer solution, assuming all notes start at end condition temp"""
    dx = distance / nodes

    # Stability estimate
    if dt is None:
        dt = dx**2 / (2 * diffusivity)
        print(f"FDM Dt: {dt}")

    d = np.arange(0, distance, dx)
    time = np.arange(0, max_time, dt)
    temps = np.zeros_like(d) + end_t

    temp_history = np.zeros((len(time), len(d)))

    # THIS IS NOT OPTIMZED... CAN BE VECTORIZED BUT I AM LAZY
    # Boundary conditions
    temps[0] = start_t

    for i,_ in tqdm(enumerate(time), total=len(time)):
        for j,t in enumerate(temps):

            # Skip start and finish
            if j == 0 or j == len(temps) - 1:
                continue

            if method == 'explicit':
                temp_history[i][j] = fdm_newT_explicit(diffusivity, temps[j + 1], temps[j], temps[j - 1], dx, dt)

            elif method == "rk4":
                dTdt = fdm_dT_dt(diffusivity, temps[j + 1], temps[j], temps[j - 1], dx)
                temp_history[i][j] = np_rk4([dTdt, temps[j]],dt)

        temp_history[i] = temps

    time = time[::int(max_time/(dt*20))]

    # Create initial plot
    fig = go.Figure()

    # NOT CLEAN HAHA but who cares
    if not imperial_results:

        # Add initial trace (only the first temperature vs distance graph)
        fig.add_trace(go.Heatmap(z=temp_history[0], y=[time[0]] * len(d), x=d, colorscale='Viridis'))

        # Add scrollbar
        fig.update_layout(
            title="Temperature vs Distance",
            xaxis_title="Distance [m]",
            yaxis_title="Temperature [degK]",
            sliders=[{
                "active": 0,
                "steps": [{"label": f"Time: {t}", "method": "update", "args": [{"z": [temp_history[i]]}, {"title": f"Temperature vs Distance - Time: {t}"}]} for i, t in enumerate(time)],
                "pad": {"t": 50},
                "currentvalue": {"visible": True, "prefix": "Time: "},
                "transition": {"duration": 300, "easing": "cubic-in-out"}
            }]
        )
    else:

        # Add initial trace (only the first temperature vs distance graph)
        fig.add_trace(go.Heatmap(z=convert(temp_history[0], 'degK', 'degF'), y=[time[0]] * len(d), x=convert(d, 'm', 'in'), colorscale='Viridis'))

        # Add scrollbar
        fig.update_layout(
            title="Temperature vs Distance",
            xaxis_title="Distance [in]",
            yaxis_title="Temperature [degF]",
            sliders=[{
                "active": 0,
                "steps": [{"label": f"Time: {t}", "method": "update", "args": [{"z": [temp_history[i]]}, {"title": f"Temperature vs Distance - Time: {t}"}]} for i, t in enumerate(time)],
                "pad": {"t": 50},
                "currentvalue": {"visible": True, "prefix": "Time: "},
                "transition": {"duration": 300, "easing": "cubic-in-out"}
            }]
        )
    if export_path is not None:
        fig.write_html(export_path)

    fig.show()


