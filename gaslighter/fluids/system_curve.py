import numpy as np
from CoolProp.CoolProp import PropsSI

from gaslighter import DataStorage

from .general import velocity_from_mdot


def system_curve_incompressible(
    flow_obj_dict: dict[str, object],
    total_source_pressure: float,
    total_source_temperature: float,
    mdot_start: float,
    mdot_end: float,
    increments: float = 1e-3,
) -> DataStorage:
    """Generates a system curve for incompressible objects"""

    data: DataStorage = DataStorage.from_arange(
        mdot_start, mdot_end, increments, "mdot [kg/s]", name="System Curve"
    )

    # Grab first key and fluid defintiion
    fluid = flow_obj_dict[list(flow_obj_dict.keys())[0]].fluid

    # Go through each component
    for mdot in data.time_array_s:

        total_pressure_drop = 0

        for name, flow_obj in flow_obj_dict.items():

            if flow_obj.fluid != fluid:
                raise ValueError(
                    f"ERROR| [{name}: {flow_obj.fluid}] fluid does not match first fluid in list [{fluid}]"
                )

            upstream_press = total_source_pressure - total_pressure_drop

            if upstream_press > 0:
                density = PropsSI(
                    "D", "P", upstream_press, "T", total_source_temperature, fluid
                )
            else:
                density = 0

            component_dp = flow_obj.dp(mdot, upstream_press, total_source_temperature)

            data.record_data(f"{name}.upstream_presure [Pa]", upstream_press)

            data.record_data(f"{name}.dp [dPa]", component_dp)

            data.record_data(
                f"{name}.velocity [m/s]",
                velocity_from_mdot(mdot, density, flow_obj.area),
            )

            total_pressure_drop += component_dp

        data.record_data(f"System Pressure Drop [dPa]", total_pressure_drop)
        data.record_data(
            f"System Outlet Pressure [dPa]", total_source_pressure - total_pressure_drop
        )
        data.next_cycle()

    return data
