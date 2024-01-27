import faulthandler

faulthandler.enable()

from thrusty import *
from thrusty import fluids

data = DataStorage(
    1e-3,
    100.0
)

tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure = convert(200.0, 'psia', 'Pa'),
    temp = STD_ATM_K,
    volume = convert(1, 'gal', 'm^3'),
    fluid = "air"
)

for t in data.time_array_s:
    # Stop the sim if tank pressure matches atmospheric
    if tank.state.presure <= STD_ATM_PA + 100:
        break

    # Caluclate mdot from nozzel [need model]
    mdot = -0.09 + (np.sin(t) * 0.1)

    # Calculate change in energy which in this case = internal energy only
    udot = mdot * tank.state.sp_enthalpy

    # Integrate udot and mdot
    new_mass = np_rk4([mdot, tank.mass], data.dt_s)
    new_inenergy = np_rk4([udot, tank.inenergy], data.dt_s)

    # Try a real gas lookup, update state properties
    try:
        tank.update_mu(new_mass, new_inenergy)

    # If you get a lookup error, stop the sim and pint it out
    except ValueError as e:
        print(e)
        break


    # Record Results
    data.record_list(
        [
            ("mdot [kg/s]", mdot),
            ("udot [J/s]", udot),
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