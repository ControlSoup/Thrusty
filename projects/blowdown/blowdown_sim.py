import plotly.graph_objects as go
from tqdm import tqdm

from gaslighter import *
from gaslighter import fluids

data = DataStorage(1e-3, 40.0)

# 1/4" fitting blowing out a tank
orifice_diameter_in = 0.125
tank_pressure_psia = 1000.0
tank_volume_gal = 1.0

cd = 0.7
orifice_diameter = convert(orifice_diameter_in, "in", "m")
cda = cd * circle_area_from_diameter(orifice_diameter)

# -----------------------------------------------------------------------------
# Pure Isentropic Example
# -----------------------------------------------------------------------------
tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure=convert(tank_pressure_psia, "psia", "Pa"),
    temp=STD_ATM_K,
    volume=convert(tank_volume_gal, "gal", "m^3"),
    fluid="N2O",
)

for t in tqdm(data.time_array_s):

    # Mass flow given dp across fitting
    mdot = -fluids.ideal_orifice_mdot(cda, tank.state, STD_ATM_PA)

    # Stop if no flow
    if mdot == 0.0:
        break

    # Integrate mdot
    new_mass = np_rk4([mdot, tank.mass], data.dt_s)

    # Calc new density
    new_density = new_mass / tank.volume

    # try a new state lookup
    try:
        new_tank_state = tank.state.isentropic("D", new_density)
    except ValueError as e:
        print(e)
        break

    # Update mass and energy
    tank.update_mu(new_mass, new_tank_state.sp_inenergy * new_mass)

    # Record Results
    data.record_from_list(
        [
            ("isentropic_mdot [kg/s]", mdot),
            ("isentropic_tank.mass [kg]", tank.mass),
            ("isentropic_tank.volume [m^3]", tank.volume),
            ("isentropic_tank.inenergy [J]", tank.inenergy),
            ("isentropic_tank.pressure [Pa]", tank.state.pressure),
            ("isentropic_tank.temperature [degK]", tank.state.temp),
            ("isentropic_tank.density [kg/m^3]", tank.state.density),
            ("isentropic_tank.sp_inenergy [J/kg]", tank.state.sp_inenergy),
            ("isentropic_tank.sp_enthalpy [J/kg]", tank.state.sp_enthalpy),
        ]
    )
    data.next_cycle()

data.export_to_csv("results/isentropic.csv")
isentropic = data.datadict
data.reset(confirm=True)

# -----------------------------------------------------------------------------
# Pure Isothermal Example
# -----------------------------------------------------------------------------
tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure=convert(tank_pressure_psia, "psia", "Pa"),
    temp=STD_ATM_K,
    volume=convert(tank_volume_gal, "gal", "m^3"),
    fluid="nitrogen",
)

for t in tqdm(data.time_array_s):

    # Mass flow given dp across fitting
    mdot = -fluids.ideal_orifice_mdot(cda, tank.state, STD_ATM_PA)

    # Stop if no flow
    if mdot == 0.0:
        break

    # Integrate mdot
    new_mass = np_rk4([mdot, tank.mass], data.dt_s)

    # Calc new density
    new_density = new_mass / tank.volume

    # try a new state lookup
    try:
        new_tank_state = tank.state.isothermal("D", new_density)
    except ValueError as e:
        print(e)
        break

    # Update mass and energy
    tank.update_mu(new_mass, new_tank_state.sp_inenergy * new_mass)

    # Record Results
    data.record_from_list(
        [
            ("isothermal_mdot [kg/s]", mdot),
            ("isothermal_tank.mass [kg]", tank.mass),
            ("isothermal_tank.volume [m^3]", tank.volume),
            ("isothermal_tank.inenergy [J]", tank.inenergy),
            ("isothermal_tank.pressure [Pa]", tank.state.pressure),
            ("isothermal_tank.temperature [degK]", tank.state.temp),
            ("isothermal_tank.density [kg/m^3]", tank.state.density),
            ("isothermal_tank.sp_inenergy [J/kg]", tank.state.sp_inenergy),
            ("isothermal_tank.sp_enthalpy [J/kg]", tank.state.sp_enthalpy),
        ]
    )
    data.next_cycle()

data.export_to_csv("results/isothermal.csv")
isothermal = data.datadict
data.reset(confirm=True)

# -----------------------------------------------------------------------------
# Pure Isenthalpic Example
# -----------------------------------------------------------------------------
tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure=convert(tank_pressure_psia, "psia", "Pa"),
    temp=STD_ATM_K,
    volume=convert(tank_volume_gal, "gal", "m^3"),
    fluid="nitrogen",
)

for t in tqdm(data.time_array_s):

    # Mass flow given dp across fitting
    mdot = -fluids.ideal_orifice_mdot(cda, tank.state, STD_ATM_PA)

    # Stop if no flow
    if mdot == 0.0:
        break

    # Integrate mdot
    new_mass = np_rk4([mdot, tank.mass], data.dt_s)

    # Calc new density
    new_density = new_mass / tank.volume

    # try a new state lookup
    try:
        new_tank_state = tank.state.isenthalpic("D", new_density)
    except ValueError as e:
        print(e)
        break

    # Update mass and energy
    tank.update_mu(new_mass, new_tank_state.sp_inenergy * new_mass)

    # Record Results
    data.record_from_list(
        [
            ("isenthalpic_mdot [kg/s]", mdot),
            ("isenthalpic_tank.mass [kg]", tank.mass),
            ("isenthalpic_tank.volume [m^3]", tank.volume),
            ("isenthalpic_tank.inenergy [J]", tank.inenergy),
            ("isenthalpic_tank.pressure [Pa]", tank.state.pressure),
            ("isenthalpic_tank.temperature [degK]", tank.state.temp),
            ("isenthalpic_tank.density [kg/m^3]", tank.state.density),
            ("isenthalpic_tank.sp_inenergy [J/kg]", tank.state.sp_inenergy),
            ("isenthalpic_tank.sp_enthalpy [J/kg]", tank.state.sp_enthalpy),
        ]
    )
    data.next_cycle()

data.export_to_csv("results/isenthalpic.csv")
isenthalpic = data.datadict
data.reset(confirm=True)

# -----------------------------------------------------------------------------
# Conservation of Mass and Energy Example
# -----------------------------------------------------------------------------
tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure=convert(tank_pressure_psia, "psia", "Pa"),
    temp=STD_ATM_K,
    volume=convert(tank_volume_gal, "gal", "m^3"),
    fluid="nitrogen",
)

for t in tqdm(data.time_array_s):

    # Mass flow given dp across fitting
    mdot = -fluids.ideal_orifice_mdot(cda, tank.state, STD_ATM_PA)

    # Stop if no flow
    if mdot == 0.0:
        break

    # Change in energy, which has no external work so must be internal energy
    udot = mdot * tank.state.sp_enthalpy

    # Integrate mdot and udto
    new_mass = np_rk4([mdot, tank.mass], data.dt_s)
    new_energy = np_rk4([udot, tank.inenergy], data.dt_s)

    # try a new state lookup
    try:
        new_tank_state = tank.update_mu(new_mass, new_energy)
    except ValueError as e:
        print(e)
        break

    # Record Results
    data.record_from_list(
        [
            ("conservation_mdot [kg/s]", mdot),
            ("conservation_tank.mass [kg]", tank.mass),
            ("conservation_tank.volume [m^3]", tank.volume),
            ("conservation_tank.inenergy [J]", tank.inenergy),
            ("conservation_tank.pressure [Pa]", tank.state.pressure),
            ("conservation_tank.temperature [degK]", tank.state.temp),
            ("conservation_tank.density [kg/m^3]", tank.state.density),
            ("conservation_tank.sp_inenergy [J/kg]", tank.state.sp_inenergy),
            ("conservation_tank.sp_enthalpy [J/kg]", tank.state.sp_enthalpy),
        ]
    )
    data.next_cycle()

data.export_to_csv("results/conservation.csv")
conservation = data.datadict

# Combine all data
# Plotting
fig = go.Figure()
results = isentropic | isothermal | isenthalpic | conservation

plotting.graph_by_key(
    fig=fig,
    title="Compare Mdot, Pressure and Temp",
    datadict=results,
    x_key="time [s]",
    key_list=[
        "isentropic_mdot [kg/s]",
        "isentropic_tank.pressure [Pa]",
        "isentropic_tank.temperature [degK]",
        "isothermal_mdot [kg/s]",
        "isothermal_tank.pressure [Pa]",
        "isothermal_tank.temperature [degK]",
        "isenthalpic_mdot [kg/s]",
        "isenthalpic_tank.pressure [Pa]",
        "isenthalpic_tank.temperature [degK]",
        "conservation_mdot [kg/s]",
        "conservation_tank.pressure [Pa]",
        "conservation_tank.temperature [degK]",
    ],
    show_fig=False,
    export_path="results/mdot_p_t_comparision.html",
)

# Plot all
fig = go.Figure()
plotting.graph_datadict(
    fig=fig,
    title="Blowdown",
    datadict=results,
    x_key="time [s]",
    show_fig=False,
    export_path="results/blowdown.html",
)
fig.show()
