from CoolProp.CoolProp import PropsSI

from gaslighter import STD_ATM_PA, circle_area_from_diameter, convert
from gaslighter.fluids import (
    IncompressibleOrifice,
    IncompressiblePipe,
    system_curve_incompressible,
)

# This Nos ladder is an example of why traditional pressure ladders dont work for low vapor presure flow objects
nos_pressure = convert(1000, "psia", "Pa")
nos_list = {
    "FeedPipe": IncompressiblePipe(
        convert(1, "in", "m"), roughness=0.001, length=1, fluid="N2O"
    ),
    # "Injector": IncompressibleOrifice(
    #     cd=7,
    #     area=circle_area_from_diameter(convert(0.04, 'in', 'm')),
    #     fluid="N2O"
    # ),
}
nos_data = system_curve_incompressible(
    nos_list,
    total_source_pressure=nos_pressure,
    total_source_temperature=PropsSI("T", "P", nos_pressure, "Q", 1.0, "N2O") + 1,
    mdot_start=convert(0.8, "lbm/s", "kg/s"),
    mdot_end=convert(1.2, "lbm/s", "kg/s"),
)
nos_data.plot_imperial(title="NOS Pressure Drop")
