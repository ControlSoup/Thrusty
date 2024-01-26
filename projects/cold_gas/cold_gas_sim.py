from thrusty import *
from thrusty import fluids

data = DataStorage(
    1e-1,
    100.0
)

tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure = convert(200.0, 'psia', 'Pa'),
    temp = STD_ATM_K,
    volume = convert(1, 'gal', 'm^3'),
    fluid = "air"
)

# Need a mdot model

for t in data.time_array_s:
    # Update mass based on current mdot
    mdot = np.sin(t) * 0.01
    new_mass = np_rk4([mdot, tank.mass], data.dt_s)

    # Conserve mass and energy
    # try:
    #     tank.update_mu(new_mass, mdot * tank.state.sp_enthalpy)
    # except ValueError as e:
    #     print(e)
    #     break

    # Record Results
    data.record_list(
        [
            ("mdot [kg/s]", mdot),
            ("tank.mass [kg]", tank.mass),
            ("tank.volume [kg]", tank.volume),
            ("tank.inenergy [J]", tank.inenergy),
            ("tank.pressure [Pa]", tank.state.presure),
            ("tank.temperature [K]", tank.state.temp),
            ("tank.density [kg/m^3]", tank.state.density),
            ("tank.sp_inenergy [J/kg]", tank.state.sp_inenergy),
            ("tank.sp_enthalpy [J/kg]", tank.state.sp_enthalpy),
        ]
    )
    data.next_cycle()

data.export_to_csv("test.csv")
data.plot_all()