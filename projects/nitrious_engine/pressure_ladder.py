from CoolProp.CoolProp import PropsSI

from gaslighter import STD_ATM_K, STD_ATM_PA,circle_area_from_diameter, convert, fluids

# ==============================================================================
# Ipa
# ==============================================================================

ipa_set_pressure = convert(220, "psia", "Pa")
ipa_comps = {
    "Sump": fluids.IncompressibleOrifice(
        cd=0.65, area=convert(0.5, "in", "m"), fluid="ethanol"
    ),
    "Ball Valve": fluids.IncompressibleOrifice.from_cv(cv=4.8, fluid="ethanol"),
    "Outlet pipe": fluids.IncompressiblePipe(
        diameter=convert(0.5, "in", "m"), roughness=0.003, length=3, fluid="ethanol"
    ),
    "Injector Flex Pipe": fluids.IncompressiblePipe(
        number_of=2,
        diameter=convert(0.25, "in", "m"),
        roughness=0.003,
        length=0.25,
        fluid="ethanol",
    ),
    "Injector": fluids.IncompressibleOrifice(
        number_of=2,
        cd=0.65,
        area=circle_area_from_diameter(convert(0.15, "in", "m")),
        fluid="ethanol",
    ),
}
ipa_system_curve_data = fluids.system_curve_incompressible(
    ipa_comps,
    total_source_pressure=ipa_set_pressure,
    total_source_temperature=STD_ATM_K,
    mdot_start=convert(0.4, "lbm/s", "kg/s"),
    mdot_end=convert(0.8, "lbm/s", "kg/s"),
)
ipa_system_curve_data.plot_all(
    show_fig=False, export_path="plots/ipa_pressure_ladder.html"
)
ipa_system_curve_data.plot_imperial(
    show_fig=False, export_path="plots/ipa_pressure_ladder_imperial.html"
)

# ==============================================================================
# Nitrious
# ==============================================================================

n2o_sat_density = PropsSI("D", "P", convert(1000, "psia", "Pa"), "Q", 0.0, "N2O")
water_sat_density = PropsSI("D", "P", STD_ATM_PA, "Q", 0.0, "water")

expected_gpm = 11.99
mdot = convert(expected_gpm , "gal/min", "m^3/s") * n2o_sat_density

print(f"mdot [kg/s]: {mdot}")
print(f"N2O Sat Density [kg/m^3]: {n2o_sat_density}")
print(f"N2O Mdot [kg/s]: {n2o_sat_density}")
print(f"Water Sat Density [kg/m^3]: {water_sat_density}")
print(f"Sat Nitrous SG [-]: {n2o_sat_density / water_sat_density}")