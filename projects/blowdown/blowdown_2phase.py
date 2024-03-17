from gaslighter.fluids import DryerOrifice, BasicStaticVolume
from gaslighter import DataStorage, STD_ATM_K, STD_ATM_PA, convert, circle_area_from_diameter, np_rk4
from tqdm import tqdm

data = DataStorage.from_arange(
    start = 0.0,
    end = 40.0,
    dx = 1e-3
)

# 1/4" fitting blowing out a tank
orifice_diameter_in = 0.125
tank_pressure_psia = 1200.0
tank_volume_gal = 1.0

cd = 0.7
orifice_diameter = convert(orifice_diameter_in, "in", "m")
cda = cd * circle_area_from_diameter(orifice_diameter)
orifice: DryerOrifice = DryerOrifice.from_cda(cda, 'N2O', cd = cd)

# -----------------------------------------------------------------------------
# Pure Isentropic Example
# -----------------------------------------------------------------------------
tank: BasicStaticVolume = BasicStaticVolume.from_ptv(
    pressure=convert(tank_pressure_psia, "psia", "Pa"),
    temp=STD_ATM_K,
    volume=convert(tank_volume_gal, "gal", "m^3"),
    fluid="nitrogen",
)

for t in tqdm(data.data_array):

    # Mass flow given dp across fitting
    mdot = -orifice.mdot(tank.state.pressure, tank.state.temp, STD_ATM_PA)

    # Stop if no flow
    if mdot == 0.0:
        break

    # Change in energy, which has no external work so must be internal energy
    udot = mdot * tank.state.sp_enthalpy

    # Integrate mdot and udto
    new_mass = np_rk4([mdot, tank.mass], data.dx)
    new_energy = np_rk4([udot, tank.inenergy], data.dx)

    # try a new state lookup
    try:
        tank.update_mu(new_mass, new_energy)
    except ValueError as e:
        print(e)
        break

    # Record Results
    data.record_from_dict({
        "dryer_mdot [kg/s]": mdot,
        "tank.mass [kg]": tank.mass,
        "tank.volume [m^3]": tank.volume,
        "tank.inenergy [J]": tank.inenergy,
        "tank.pressure [Pa]": tank.state.pressure,
        "tank.temperature [degK]": tank.state.temp,
        "tank.density [kg/m^3]": tank.state.density,
        "tank.sp_inenergy [J/kg]": tank.state.sp_inenergy,
        "tank.sp_enthalpy [J/kg]": tank.state.sp_enthalpy,
    })
    data.next_cycle()

data.plot_imperial()
# data.export_to_csv("results/isentropic.csv")
