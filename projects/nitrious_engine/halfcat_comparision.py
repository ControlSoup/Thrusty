from gaslighter import *
from gaslighter import sutton

# Half Cat inputs form Half Cat Sim
chamber = RocketEngineCEA(
    ox="N2O",
    fuel="IPA",
    chamber_pressure=convert(261, "psia", "Pa"),
    mdot=0.906,
    MR=2.444,
    eps=2.28,
)

current_exit_length = sutton.exit_length(
    chamber.throat_diameter, np.deg2rad(15), chamber.exit_diameter
)
output = pretty_key_val("Exit Length [m]", current_exit_length, round_places=8)
output += chamber.string(round_places=8)

print(output)
to_file(output, "results/halfcat_results.md", file_name="HalfCat Comparision")

output_imperial = pretty_key_val(
    "Exit Length [in]", convert(current_exit_length, "m", "in"), round_places=4
)
output_imperial += chamber.imperial_string(round_places=8)

print(output_imperial)
to_file(output_imperial, "results/halfcat_imperial.md", file_name="HalfCat Comparision")
