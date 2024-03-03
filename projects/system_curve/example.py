from gaslighter.fluids import IncompressibleOrifice, IncompressiblePipe, system_curve_incompressible
from gaslighter import STD_ATM_PA, convert 

pipe_list = {
    "Sump": IncompressibleOrifice(
        cd = 0.65,
        area = convert(0.25, "in", "m"),
        fluid = "water"
    ),
    "Outlet Pipe": IncompressiblePipe(
        diameter = convert(0.25, "in", "m"),
        roughness = 0.003,
        length = 1,
        fluid = 'water'
    ),
    "Injector": IncompressibleOrifice(
        cd = 0.65,
        area = convert(3, "mm", "m"),
        fluid = "water"
    ),
}

data = system_curve_incompressible(
    pipe_list,
    total_source_pressure=convert(200, 'psia', 'Pa'),
    total_source_temperature=280,
    mdot_start = 0.01,
    mdot_end = 0.25 
)
data.plot_imperial()