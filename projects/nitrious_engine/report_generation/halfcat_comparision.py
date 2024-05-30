import numpy as np
from gaslighter import *
from gaslighter import sutton

# Half Cat inputs form Half Cat Sim
throat_diameter = convert(1, "in", "m")
exit_diameter = convert(2, "in", "m")
cstar_efficency = 0.70
halfcat: RocketEngineGeometry = RocketEngineGeometry(
    chamber_diameter=convert(2, "in", "m"),
    chamber_length=convert(5, "in", "m"),
    chamber_volume=2.6e-4,
    throat_diameter=throat_diameter,
    exit_diameter=exit_diameter,
    exit_length=sutton.exit_length(throat_diameter, np.deg2rad(20), exit_diameter)
)

chamber = RocketEngineCEA(
    ox="N2O",
    fuel="IPA",
    chamber_pressure=convert(255, "psia", "Pa"),
    mdot=0.883,
    MR=2.605,
    eps=halfcat.expansion_ratio,
    thrust_efficency_fraction = halfcat.half_angle_losses * cstar_efficency
)

output = chamber.dict
output = output | halfcat.dict()
output = sort_dict(output)
to_file(
    pretty_dict(output),
    "../results/halfcat_comparison.md",
    file_name="Halfcat Comparision",
)

output = imperial_dictionary(output)
output = sort_dict(output)
to_file(
    pretty_dict(output),
    "../results/halfcat_comparison_imperial.md",
    file_name="Halfcat Comparision Imperial",
)