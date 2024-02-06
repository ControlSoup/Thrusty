from gaslighter import fluids
from gaslighter import *

chamber = fluids.RocketChamber(
    'N2O', 'IPA', convert(150, 'psia', 'Pa')
)

pressure_data = chamber.pressure_study(
    convert(10, 'psia', 'Pa'),
    convert(1000, 'psia', 'Pa'),
)
graph_datadict(pressure_data, 'Chamber Pressure [Pa]', title=f'Pressure Sweep [{chamber.ox},{chamber.fuel}]')
mix_data = chamber.mix_study()
graph_datadict(mix_data, 'Mix Ratio [-]',title=f'Mix Sweep [{chamber.ox},{chamber.fuel}]')

chamber.pressure_mix_contour(
    'chamber_temp',
    convert(10, 'psia', 'Pa'),
    convert(500, 'psia', 'Pa')
)