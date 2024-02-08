from gaslighter import fluids
from gaslighter import *

# Make a base chamber
chamber = fluids.RocketChamber(
    'N2O', 'IPA', convert(150, 'psia', 'Pa')
)

# Get Pressure data
pressure_data = chamber.pressure_study(
    convert(10, 'psia', 'Pa'),
    convert(1000, 'psia', 'Pa'),
)

# Graph pressure data
graph_datadict(pressure_data, 'Chamber Pressure [Pa]', title=f'Pressure Sweep [{chamber.ox},{chamber.fuel}]')

# Get Mix data
mix_data = chamber.mix_study()

# Graph mix data
graph_datadict(mix_data, 'Mix Ratio [-]',title=f'Mix Sweep [{chamber.ox},{chamber.fuel}]')

# Plot any contour on pressure vs mix ratio in the chamber class (see @prameters)
chamber.pressure_mix_contour(
    ['chamber_temp','isp','cstar'],
    convert(10, 'psia', 'Pa'),
    convert(100, 'psia', 'Pa'),
    export_path="contours.html"
)