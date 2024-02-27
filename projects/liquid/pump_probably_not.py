import matplotlib.pyplot as plt
import numpy as np

from gaslighter import *


def mdot_to_total_mdot(mdot):
    return mdot + (2.5 * mdot)


def contour(mdot, psia):
    gamma = 1.2
    sp_R = 242
    total_mdot = mdot = mdot_to_total_mdot(mdot)
    velocity = exit_velocity(
        gamma,
        sp_R,
        convert(psia, "psia", "Pa"),
        chamber_temp=1033,
        exit_pressure=STD_ATM_PA,
    )
    force = total_mdot * velocity
    return convert(force, "N", "lbf")


mdot_range = np.linspace(0, 1, 100)
psia_range = np.linspace(100, 800, 100)
mdot, psia = np.meshgrid(mdot_range, psia_range)

z = contour(mdot, psia)

# Create 3D contour plot
fig = go.Figure(data=[go.Surface(z=z, x=mdot, y=psia)])
fig.update_layout(
    scene=dict(
        xaxis_title="mdot[kg/s]", yaxis_title="psia [psia]", zaxis_title="force [lbf]"
    )
)
fig.show()
