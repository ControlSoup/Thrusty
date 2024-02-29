from gaslighter.fluids import IncompressibleOrifice, IncompressiblePipe, system_curve_isothermal_incompressible
from gaslighter import STD_ATM_PA



pipe_list = {
    "Cv 0.5": IncompressibleOrifice.from_cv(1, "water"),
    "Cv 1.0": IncompressibleOrifice.from_cv(0.5, "water"),
    "Pipe 3m": IncompressiblePipe.from_relative_roughness(
        0.00001,
        0.00000001,
        3,
        'water'
    ),
}

data = system_curve_isothermal_incompressible(
    pipe_list,
    100 * STD_ATM_PA,
    280,
    0.1,
    5,
    0.001
)

data.plot_all()