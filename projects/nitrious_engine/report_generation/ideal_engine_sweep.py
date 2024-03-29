from gaslighter import *

# Ideal Engine Configuration
chamber: rocket_engines.RocketEngineCEA = rocket_chamber.RocketEngineCEA.from_fuelmdot(
    ox="N2O",
    fuel="IPA",
    chamber_pressure=convert(150, "psia", "Pa"),
    fuel_mdot=convert(0.1, "gal", "m^3") * 778,  # Convert 0.5gal/5s of ipa to mdot
    MR=1.6,
    eps=2.3,
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
)

# Mixture ratio graph
mix_data = chamber.mix_study(start_mix_ratio_ratio=1.05, end_mix_ratio_ratio=3.0)
graph_datadict(
    mix_data,
    "Mix Ratio [-]",
    title=f"Mix Sweep [{chamber.ox},{chamber.fuel}]",
    export_path="../plots/ideal_mixratio_sweep.html",
)

# Expansion Ratio Graph
eps_data = chamber.eps_study(start_eps=1.1, end_eps=3.0)
graph_datadict(
    eps_data,
    "Area Expansion Ratio [-]",
    title=f"Eps Sweep [{chamber.ox},{chamber.fuel}]",
    export_path="../plots/ideal_esps_sweep.html",
)

# Mdot Graph
mdot_data = chamber.mdot_study(start_mdot=0.5, end_mdot=1.0)
graph_datadict(
    mdot_data,
    "mdot [kg/s]",
    title=f"Mdot Sweep [{chamber.ox},{chamber.fuel}]",
    export_path="../plots/ideal_mdot_sweep.html",
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
to_file(output, "results/ideal_results.md", file_name="Ideal Engine Results")

# Convert to imperial
output_imperial = chamber.imperial_string(round_places=8)

print(output_imperial)
to_file(
    output_imperial,
    "../results/ideal_engine_results_imperial.md",
    file_name="Current Engine Results",
)
