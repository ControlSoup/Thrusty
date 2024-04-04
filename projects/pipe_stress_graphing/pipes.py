from gaslighter import *
from gaslighter.asme import b313
from gaslighter.structrual import thin_wall_hoop_pressure

# Material Properies
outer_diameter = convert(0.5, "in", "m")
allowable_tensile = b313.table_a1_stress("COPPER", STD_ATM_K)
copper_handbook = convert(10300, "psi", "Pa")

data: DataStorage = DataStorage.from_arange(
    convert(0.005, "in", "m"), 
    0.99 * outer_diameter, 
    convert(0.001, "in", "m"),
    data_key = "Thickness [m]"
)


for t in data.data_array:
    pressure = b313.pipe_pressure(
        thickness=t,
        outside_diameter=outer_diameter,
        allowable_tensile=copper_handbook,
        quality_factor=0.8,
    )

    data.record(
        "B31.3 Pressure [Pa]", 
        pressure
    )

    data.record("Allowable Tensile [Pa]", allowable_tensile)
    data.record(
        "Hoop Pressure ASME Stress [Pa]",
        thin_wall_hoop_pressure(
            copper_handbook,
            outer_diameter / 2.0,
            t
        )
    )
    data.record(
        "Hoop Pressure Lookup Stress [Pa]",
        thin_wall_hoop_pressure(
            convert(30500, "psia", "Pa"),
            outer_diameter / 2.0,
            t
        )
    )

    data.next_cycle()

data.plot_imperial(title=f"{convert(outer_diameter, 'm', 'in')} [in] OD Pipe, ")