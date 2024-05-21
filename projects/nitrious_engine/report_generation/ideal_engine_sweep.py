from gaslighter import *
from gaslighter.fluids import DryerOrifice

# Copy pasta of nos injector stuff
cd = 0.63  # <- need data
orifice_diameter_m = convert(0.1520, "in", "m")
nitrous_injector: DryerOrifice = DryerOrifice(
    cd=cd,
    area=circle_area_from_diameter(orifice_diameter_m),
    fluid="N2O"
)

# Lazy way to get a fit
ipa_system_curve_data = csv_to_datadict('../data/ipa_pressure_ladder.csv')

def fuel_mdot_from_chamber_pressure(chamber_pressure: float):
    # This really should be a poly fit
    target_index = np_within_tolerance(ipa_system_curve_data['System Outlet Pressure [Pa]'], chamber_pressure, 1000)
    return ipa_system_curve_data['mdot [kg/s]'][target_index]

def ox_mdot_from_chamber_pressure(chamber_pressure: float):
    return nitrous_injector.mdot(convert(1000.0, 'psia', 'Pa'), convert(70, 'degF', 'degK'), chamber_pressure)

# Ideal Engine Configuration
chamber_pressure = convert(150, "psia", "Pa")
chamber: rocket_engines.RocketEngineCEA = rocket_chamber.RocketEngineCEA.from_mdots(
    ox="N2O",
    fuel="IPA",
    chamber_pressure=chamber_pressure,
    fuel_mdot=fuel_mdot_from_chamber_pressure(chamber_pressure),  # Convert 0.5gal/5s of ipa to mdot
    ox_mdot = ox_mdot_from_chamber_pressure(chamber_pressure),
    eps=2.5,
)
# Pressure Graphs
pressure_data = chamber.pressure_study(
    convert(100, "psia", "Pa"),
    convert(300, "psia", "Pa"),
)
graph_datadict(
    pressure_data,
    "Chamber Pressure [Pa]",
    title=f"Pressure Sweep [{chamber.ox},{chamber.fuel}]",
    export_path="../plots/ideal_pressure_sweep.html",
    show_fig=False
)

# Mixture ratio graph
mix_data = chamber.mix_study(start_mix_ratio_ratio=1.05, end_mix_ratio_ratio=10.0)
graph_datadict(
    mix_data,
    "Mix Ratio [-]",
    title=f"Mix Sweep [{chamber.ox},{chamber.fuel}]",
    export_path="../plots/ideal_mixratio_sweep.html",
    show_fig=False
)

# Expansion Ratio Graph
eps_data = chamber.eps_study(start_eps=1.1, end_eps=3.0)
graph_datadict(
    eps_data,
    "Area Expansion Ratio [-]",
    title=f"Eps Sweep [{chamber.ox},{chamber.fuel}]",
    export_path="../plots/ideal_esps_sweep.html",
    show_fig=False
)

# Expansion Ratio Graph
throat_data = chamber.throat_errosion_study(
    chamber.throat_diameter,
    chamber.throat_diameter * 2,
    ox_mdot_from_chamber_pressure,
    fuel_mdot_from_chamber_pressure
)
graph_datadict(
    throat_data,
    "Throat Diameter [m]",
    title=f"Throat Errosion [{chamber.ox},{chamber.fuel}]",
    export_path="../plots/ideal_throat_errosion.html",
    show_fig=False
)
graph_datadict(
    imperial_dictionary(throat_data),
    "Throat Diameter [in]",
    title=f"Eps Sweep [{chamber.ox},{chamber.fuel}]",
    export_path="../plots/ideal_throat_errosion_imperial.html",
    show_fig=False
)

# Mdot Graph
mdot_data = chamber.mdot_study(start_mdot=0.5, end_mdot=1.0)
graph_datadict(
    mdot_data,
    "mdot [kg/s]",
    title=f"Mdot Sweep [{chamber.ox},{chamber.fuel}]",
    export_path="../plots/ideal_mdot_sweep.html",
    show_fig=False
)

# Plot any contour on pressure vs mix ratio in the chamber class (see @prameters)
chamber.pressure_mix_contour(
    ["chamber_temp", "isp", "cstar"],
    convert(100, "psia", "Pa"),
    convert(200, "psia", "Pa"),
    start_mix_ratio=1.8,
    end_mix_ratio=3.0,
    export_path="../plots/ideal_",
    show_plot=False,
)

# Plot contour on pressure vs eps in the chamber class (see @prameters)
chamber.pressure_eps_contour(
    ["chamber_temp", "isp", "cstar", "exit_pressure"],
    convert(100, "psia", "Pa"),
    convert(200, "psia", "Pa"),
    start_eps=1.1,
    end_eps=5,
    export_path="../plots/ideal_",
    show_plot=False,
)

# Calculate External geomtry stuff
output = chamber.string(round_places=8)

print(output)
to_file(output, "../results/ideal_results.md", file_name="Ideal Engine Results")

# Convert to imperial
output_imperial = chamber.imperial_string(round_places=8)

print(output_imperial)
to_file(
    output_imperial,
    "../results/ideal_engine_results_imperial.md",
    file_name="Current Engine Results",
)
