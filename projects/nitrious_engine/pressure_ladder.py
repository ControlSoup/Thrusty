from CoolProp.CoolProp import PropsSI
from gaslighter import STD_ATM_K, circle_area_from_diameter, convert, fluids

ipa_set_pressure = convert(200, "psia", "Pa")
ipa_comp_list = {
    "Sump": fluids.IncompressibleOrifice(
        cd=0.65, area=convert(0.5, "in", "m"), fluid="ethanol"
    ),
    "Ball Valve": fluids.IncompressibleOrifice.from_cv(cv=4.8, fluid="ethanol"),
    "Outlet pipe": fluids.IncompressiblePipe(
        diameter=convert(0.444, "in", "m"), roughness=0.0015e-3, length=1.5, fluid="ethanol"
    ),
    "Injector Flex Pipe": fluids.IncompressiblePipe(
        number_of=2,
        diameter=convert(0.375, "in", "m"),
        roughness=0.003,
        length=0.25,
        fluid="ethanol",
    ),
    "Injector": fluids.IncompressibleOrifice(
        number_of=2,
        cd=0.65,
        area=circle_area_from_diameter(convert(0.155, "in", "m")),
        fluid="ethanol",
    ),
}
ipa_system_curve_data = fluids.system_curve_incompressible(
    ipa_comp_list,
    total_source_pressure=ipa_set_pressure,
    total_source_temperature=STD_ATM_K,
    mdot_start=convert(0.1, "lbm/s", "kg/s"),
    mdot_end=convert(1.5, "lbm/s", "kg/s"),
    increments=1e-4
)
ipa_system_curve_data.plot_all(show_fig=False, export_path='plots/ipa_pressure_ladder.html')
ipa_system_curve_data.plot_imperial(show_fig=True, export_path='plots/ipa_pressure_ladder_imperial.html')
ipa_system_curve_data.export_to_csv("data/ipa_pressure_ladder.csv")
