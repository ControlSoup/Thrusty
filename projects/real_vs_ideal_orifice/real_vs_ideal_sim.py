import plotly.graph_objects as go
from tqdm import tqdm

from gaslighter import *
from gaslighter import fluids
from CoolProp.CoolProp import PropsSI

# Constants
FLUID = "nitrogen"

data: DataStorage = DataStorage.from_arange(start=0.0, end=150.0, dx=1e-3)

# 1/4" fitting blowing out a tank
orifice_diameter_in = 0.25
tank_pressure_psia = 3000
tank_temperature_degF = 150
tank_volume_gal = 1.0

cd = 0.7
orifice_diameter = convert(orifice_diameter_in, "in", "m")
cda = cd * circle_area_from_diameter(orifice_diameter)

# -----------------------------------------------------------------------------
#  Real Conservation
# -----------------------------------------------------------------------------
tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure=convert(tank_pressure_psia, "psia", "Pa"),
    temp=convert(tank_temperature_degF, 'degF', 'degK'),
    volume=convert(tank_volume_gal, "gal", "m^3"),
    fluid=FLUID,
)

for t in tqdm(data.data_array):

    # Mass flow given dp across fitting
    try:
        mdot, is_choked = fluids.real_orifice_mdot(
            cda, tank.state, STD_ATM_PA, verbose_return=True
        )
    except ValueError as e:
        print(e)
        break

    # Stop if no flow
    if mdot == 0.0:
        break

    # Change in energy, which has no external work so must be internal energy
    try:
        udot = mdot * tank.state.sp_enthalpy
    except Exception as e:
        udot = mdot * PropsSI("HMASS", 'P', tank.state.pressure, 'T', tank.state.temp, tank.state.fluid)

    # Integrate mdot and udot
    new_mass = np_rk4([-mdot, tank.mass], data.dx)
    new_energy = np_rk4([-udot, tank.inenergy], data.dx)

    # try a new state lookup
    try:
        new_tank_state = tank.update_mu(new_mass, new_energy)
    except ValueError as e:
        print(e)
        break

    # Record Results
    data.record_from_dict(
        {
            "real_mdot [kg/s]": mdot,
            "real_is_choked [-]": is_choked,
            "real_tank.mass [kg]": tank.mass,
            "real_tank.volume [m^3]": tank.volume,
            "real_tank.inenergy [J]": tank.inenergy,
            "real_tank.pressure [Pa]": tank.state.pressure,
            "real_tank.temperature [degK]": tank.state.temp,
            "real_tank.density [kg/m^3]": tank.state.density,
            "real_tank.sp_inenergy [J/kg]": tank.state.sp_inenergy,
            "real_tank.sp_enthalpy [J/kg]": tank.state.sp_enthalpy,
            "real_tank.sp_entropy [J/degK]": tank.state.sp_entropy,
            "atmospheric.pressure [Pa]": STD_ATM_PA,
        }
    )
    data.next_cycle()

real = data.datadict

data: DataStorage = DataStorage.from_arange(start=0.0, end=150.0, dx=1e-3)
# -----------------------------------------------------------------------------
#  Ideal Conservation
# -----------------------------------------------------------------------------
tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure=convert(tank_pressure_psia, "psia", "Pa"),
    temp=convert(tank_temperature_degF, 'degF', 'degK'),
    volume=convert(tank_volume_gal, "gal", "m^3"),
    fluid=FLUID,
)

for t in tqdm(data.data_array):

    # Mass flow given dp across fitting
    mdot, is_choked = fluids.ideal_orifice_mdot(
        cda, tank.state, STD_ATM_PA, verbose_return=True
    )

    # Stop if no flow
    if mdot == 0.0:
        break

    # Change in energy, which has no external work so must be internal energy
    udot = mdot * tank.state.sp_enthalpy

    # Integrate mdot and udot
    new_mass = np_rk4([-mdot, tank.mass], data.dx)
    new_energy = np_rk4([-udot, tank.inenergy], data.dx)

    # try a new state lookup
    try:
        new_tank_state = tank.update_mu(new_mass, new_energy)
    except ValueError as e:
        print(e)
        break

    # Record Results
    data.record_from_dict(
        {
            "ideal_mdot [kg/s]": mdot,
            "ideal_is_choked [-]": is_choked,
            "ideal_tank.mass [kg]": tank.mass,
            "ideal_tank.volume [m^3]": tank.volume,
            "ideal_tank.inenergy [J]": tank.inenergy,
            "ideal_tank.pressure [Pa]": tank.state.pressure,
            "ideal_tank.temperature [degK]": tank.state.temp,
            "ideal_tank.density [kg/m^3]": tank.state.density,
            "ideal_tank.sp_inenergy [J/kg]": tank.state.sp_inenergy,
            "ideal_tank.sp_enthalpy [J/kg]": tank.state.sp_enthalpy,
            "ideal_tank.sp_entropy [J/degK]": tank.state.sp_entropy,
            "atmospheric.pressure [Pa]": STD_ATM_PA,
        }
    )
    data.next_cycle()

ideal = data.datadict

# Combine all data
# Plotting
fig = go.Figure()
results = real | ideal

if len(results['real_mdot [kg/s]']) >= len(results["ideal_mdot [kg/s]"]):
    results["mdot_error [kg/s]"] = [(results["real_mdot [kg/s]"][i] - mdot) for i, mdot in enumerate(results['ideal_mdot [kg/s]'])]
else:
    results["mdot_error [kg/s]"] = [(results["ideal_mdot [kg/s]"][i] - mdot) for i, mdot in enumerate(results['real_mdot [kg/s]'])]

plotting.graph_by_key(
    fig=fig,
    title="Real vs Ideal Orifice",
    datadict=imperial_dictionary(results),
    x_key="time [s]",
    key_list=[
        "ideal_mdot [lbm/s]",
        "ideal_tank.pressure [psia]",
        "ideal_tank.temperature [degF]",
        "real_mdot [lbm/s]",
        "real_tank.pressure [psia]",
        "real_tank.temperature [degF]",
        "mdot_error [lbm/s]",
    ],
    show_fig=False,
    export_path="results/real_vs_ideal_ptm_comparision.html",
)

# Plot all
fig = go.Figure()
plotting.graph_datadict(
    fig=fig,
    title="Real vs Ideal Orifice",
    datadict=imperial_dictionary(results),
    x_key="time [s]",
    show_fig=True,
    export_path="results/real_vs_ideal_orifice.html",
)
