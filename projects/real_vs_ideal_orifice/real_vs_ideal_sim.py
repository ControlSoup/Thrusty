import plotly.graph_objects as go
from gaslighter import *
from gaslighter import fluids
from tqdm import tqdm
# Constants
FLUID = "helium"

data = DataStorage(1e-3, 100.0)

# 1/4" fitting blowing out a tank
orifice_diameter_in = 0.25
tank_pressure_psia = 10000
tank_volume_gal = 1.0

cd = 0.7
orifice_diameter = convert(orifice_diameter_in, "in", "m")
cda = cd * circle_area_from_diameter(orifice_diameter)

# -----------------------------------------------------------------------------
#  Real Conservation
# -----------------------------------------------------------------------------
tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure=convert(tank_pressure_psia, "psia", "Pa"),
    temp=STD_ATM_K,
    volume=convert(tank_volume_gal, "gal", "m^3"),
    fluid=FLUID,
)

for t in tqdm(data.time_array_s):

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
    udot = mdot * tank.state.sp_enthalpy

    # Integrate mdot and udot
    new_mass = np_rk4([-mdot, tank.mass], data.dt_s)
    new_energy = np_rk4([-udot, tank.inenergy], data.dt_s)


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
            "atmospheric.pressure [Pa]": STD_ATM_PA,
        }
    )
    data.next_cycle()

data.export_to_csv("results/real.csv")
real = data.datadict
data.reset(confirm=True)

# -----------------------------------------------------------------------------
#  Ideal Conservation
# -----------------------------------------------------------------------------
tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure=convert(tank_pressure_psia, "psia", "Pa"),
    temp=STD_ATM_K,
    volume=convert(tank_volume_gal, "gal", "m^3"),
    fluid=FLUID,
)

for t in tqdm(data.time_array_s):

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
    new_mass = np_rk4([-mdot, tank.mass], data.dt_s)
    new_energy = np_rk4([-udot, tank.inenergy], data.dt_s)

    # try a new state lookup
    try:
        new_tank_state = tank.update_mu(new_mass, new_energy)
    except ValueError as e:
        print(e)
        break

    # Record Results
    data.record_from_dict({
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
        "atmospheric.pressure [Pa]": STD_ATM_PA,
    })
    data.next_cycle()

data.export_to_csv("results/ideal.csv")
ideal = data.datadict

# Combine all data
# Plotting
fig = go.Figure()
results = real | ideal


results['mdot_error [kg/s]'] = np.zeros_like(results['real_mdot [kg/s]'])
for i,real in enumerate(results['real_mdot [kg/s]']):
   results['mdot_error [kg/s]'][i] = real - results['ideal_mdot [kg/s]'][i]

plotting.graph_by_key(
    fig=fig,
    title="Real vs Ideal Orifice",
    datadict=results,
    x_key="time [s]",
    key_list=[
        "ideal_mdot [kg/s]",
        "ideal_tank.pressure [Pa]",
        "ideal_tank.temperature [degK]",
        "real_mdot [kg/s]",
        "real_tank.pressure [Pa]",
        "real_tank.temperature [degK]",
        "mdot_error [kg/s]"
    ],
    show_fig=False,
    export_path="results/real_vs_ideal_ptm_comparision.html",
)

# Plot all
fig = go.Figure()
plotting.graph_datadict(
    fig=fig,
    title="Real vs Ideal Orifice",
    datadict=results,
    x_key="time [s]",
    show_fig=True,
    export_path="results/real_vs_ideal_orifice.html",
)
