from gaslighter import *
from gaslighter.fluids import DryerOrifice

report = ReportHTML(title="Ideal Engine Plots")

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
ipa_system_curve_fit = np_poly(
    ipa_system_curve_data['System Outlet Pressure [Pa]'],
    ipa_system_curve_data['mdot [kg/s]'],
    3
)

def fuel_mdot_from_chamber_pressure(chamber_pressure: float):
    if chamber_pressure < 0:
        return 0
    return ipa_system_curve_fit(chamber_pressure)

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
report.write_collapsable(
    graph_datadict(
        imperial_dictionary(pressure_data),
        "Chamber Pressure [psia]",
        show_fig=False,
        return_html=True
    ),
    section_title=f"Pressure Sweep [{chamber.ox},{chamber.fuel}]",
)

# Mixture ratio graph
mix_data = chamber.mix_study(start_mix_ratio_ratio=1.05, end_mix_ratio_ratio=10.0)
report.write_collapsable(
    graph_datadict(
        imperial_dictionary(mix_data),
        "Mix Ratio [-]",
        show_fig=False,
        return_html=True
    ),
    section_title=f"Mix Sweep [{chamber.ox},{chamber.fuel}]",
)

# Expansion Ratio Graph
eps_data = chamber.eps_study(start_eps=1.1, end_eps=3.0)
report.write_collapsable(
    graph_datadict(
        imperial_dictionary(eps_data),
        "Area Expansion Ratio [-]",
        show_fig=False,
        return_html=True
    ),
    section_title=f"Eps Sweep [{chamber.ox},{chamber.fuel}]",
)

# Throat erosion study
throat_data = chamber.throat_errosion_study(
    chamber.throat_diameter,
    chamber.throat_diameter * 2,
    ox_mdot_from_chamber_pressure,
    fuel_mdot_from_chamber_pressure
)
report.write_collapsable(
    graph_datadict(
        imperial_dictionary(throat_data),
        "Throat Diameter [in]",
        show_fig=False,
        return_html=True
    ),
    section_title=f"Throat Erosion [{chamber.ox},{chamber.fuel}]",

)

# Mdot Graph
mdot_data = chamber.mdot_study(start_mdot=0.5, end_mdot=1.0)
report.write_collapsable(
    graph_datadict(
        imperial_dictionary(mdot_data),
        "mdot [lbm/s]",
        show_fig=False,
        return_html=True
    ),
    section_title=f"Mdot Sweep [{chamber.ox},{chamber.fuel}]",
)
report.export('../plots/ideal_engine_plots.html')

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
