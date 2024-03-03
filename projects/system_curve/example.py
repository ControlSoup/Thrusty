from gaslighter.fluids import IncompressibleOrifice, IncompressiblePipe, system_curve_incompressible
from gaslighter import STD_ATM_PA, convert 


PIPE_LENGTH_M = 1
PIPE_D_M = 0.01
DENSITY_KGPM3 = 1000

pipe_list = {
    "Pipe 3m": IncompressiblePipe(
        diameter=0.01,
        roughness=0.01,
        length = 1,
        fluid='water'
    ),
}

data = system_curve_incompressible(
    pipe_list,
    total_source_pressure=100 * STD_ATM_PA,
    total_source_temperature=280,
    mdot_start = 0.1,
    mdot_end = 5
)

data.plot_all()