from gaslighter import (RocketEngineCEA, RocketEngineGeometry,
                        circle_area_from_diameter, convert,
                        imperial_dictionary, pretty_dict, sort_dict, spad,
                        to_file)

"""Generates a engine report based on true geometry"""

# Need some sim or test results for this but input mdot here
ox_mdot_result = convert(0.61, "lbm/s", "kg/s")
fuel_mdot_result = convert(1.01, "lbm/s", "kg/s")
cstar_eff = 0.7

geometry: RocketEngineGeometry = RocketEngineGeometry(
    throat_diameter=convert(1.334, "in", "m"),
    exit_diameter=convert(2.04, "in", "m"),
    chamber_diameter=convert(2.67, "in", "m"),
    chamber_length=convert(7.5, "in", "m"),
    chamber_volume=convert(7.5 * circle_area_from_diameter(2.67), "in^2", "m^2"),
    exit_length=convert(1.6, "in", "m"),
)

cea: RocketEngineCEA = RocketEngineCEA.from_geometry(
    geometry,
    ox="N2O",
    fuel="IPA",
    chamber_pressure=convert(150, "psia", "Pa"),
    ox_mdot=ox_mdot_result,
    fuel_mdot=fuel_mdot_result,
    thrust_efficency_fraction=(geometry.half_angle_losses * cstar_eff),
)

min_wall = spad.min_wall(cea.chamber_pressure, geometry.chamber_diameter / 2, 10e6)

output = cea.dict
output = output | geometry.dict()
output["Cstar Efficency [-]"] = cstar_eff
output["Min Wall [m]"] = min_wall
output = sort_dict(output)
to_file(
    pretty_dict(output),
    "../results/predicted_engine_results.md",
    file_name="Predicted Engine Results",
)

output = pretty_dict(imperial_dictionary(output))
to_file(
    output,
    "../results/predicted_engine_results_imperial.md",
    file_name="Predicted Engine Results Imperial",
)
