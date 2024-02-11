from gaslighter import fluids
from gaslighter import *

# Make a base chamber
chamber = fluids.RocketChamber(
    'N2O', 'IPA',
    convert(150, 'psia', 'Pa'),
    throat_diameter=convert(2, 'in', 'm'),
    MR=1.72,
    eps=2.28
)

# Get Pressure data
pressure_data = chamber.pressure_study(
    convert(100, 'psia', 'Pa'),
    convert(300, 'psia', 'Pa'),
)

graph_datadict(pressure_data, 'Chamber Pressure [Pa]', title=f'Pressure Sweep [{chamber.ox},{chamber.fuel}]', export_path='plots/pressure_current_nozzel.html')

# Get Mix data
mix_data = chamber.mix_study(start_mix_ratio_ratio=1.05, end_mix_ratio_ratio=3.0)

graph_datadict(mix_data, 'Mix Ratio [-]',title=f'Mix Sweep [{chamber.ox},{chamber.fuel}]', export_path='plots/mix_ratio_current_nozzel.html')

# Get eps data
eps_data = chamber.eps_study(start_eps=1.1, end_eps=3.0)

# Graph eps data
graph_datadict(eps_data, 'Area Expansion Ratio [-]',title=f'Eps Sweep [{chamber.ox},{chamber.fuel}]', export_path="plots/eps_current_nozzel.html")

# Plot any contour on pressure vs mix ratio in the chamber class (see @prameters)
chamber.pressure_mix_contour(
    ['chamber_temp', 'isp', 'cstar'],
    convert(100, 'psia', 'Pa'),
    convert(200, 'psia', 'Pa'),
    start_mix_ratio = 1.8,
    end_mix_ratio = 3.0,
    export_path = "plots/",
    show_plot = False
)

# Plot contour on pressure vs eps in the chamber class (see @prameters)
chamber.pressure_eps_contour(
    ['chamber_temp', 'isp', 'cstar', 'exit_pressure'],
    convert(10, 'psia', 'Pa'),
    convert(100, 'psia', 'Pa'),
    start_eps = 1.1,
    end_eps = 5,
    export_path = "plots/",
    show_plot=False
)

mdot = 0.15
current_thrust = thrust(mdot, chamber.exit_velocity)
ideal_throat_area = throat_area(chamber.cstar, chamber.chamber_pressure, mdot)
output = pretty_key_val("Calculated Ideal Throat Area [m^2]", ideal_throat_area, round_places=8)
output += pretty_key_val("Calculated Ideal Throat Diameter [m^2]", circle_diameter_from_area(ideal_throat_area), round_places=8)
output += pretty_key_val("Thrust [N]", current_thrust, round_places=8)
output += pretty_key_val("Exit Length [m]", exit_length(chamber.throat_diameter, np.deg2rad(15), chamber.exit_diameter), round_places=8)
output += chamber.string(round_places=8)

print(output)
to_file(output, 'current_results.md')