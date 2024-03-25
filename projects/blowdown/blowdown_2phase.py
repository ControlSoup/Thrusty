from gaslighter.fluids import DryerOrifice, BasicStaticVolume, ZillacKarabeyogluVolume, EquilibrumTank
from gaslighter import DataStorage, STD_ATM_K, STD_ATM_PA, convert, circle_area_from_diameter, np_rk4
from tqdm import tqdm
from CoolProp.CoolProp import PropsSI
from gaslighter.fluids import R_JPDEGK_MOL

data: DataStorage = DataStorage.from_arange(
    start = 0.0,
    end = 40.0,
    dx = 1e-3
)

cd = 0.7
orifice: DryerOrifice = DryerOrifice.from_cda(cda=convert(28.0, 'mm^2', 'm^2'), fluid ='N2O')

# -----------------------------------------------------------------------------
#  Equilibrium model
# -----------------------------------------------------------------------------
tank: EquilibrumTank = EquilibrumTank.from_mass(
    starting_pressure = 4.777e6,
    mass = 7.2,
    fluid='N2O'
)

for t in tqdm(data.data_array):


    # Mass flow given dp across fitting
    mdot = orifice.mdot(tank.pressure, tank.temp, STD_ATM_PA)
    try:
        tank.integrate_state(mdot, data.dx)
    except Exception:
        print(Exception)
        break

    # Stop if no flow
    if tank.total_mass <= 0.0:
        break
    if mdot == 0.0:
        break

    # Record Results
    data.record_from_dict(tank.dict())
    data.next_cycle()

data.plot_all()
data.export_to_csv("results/equilibrium_2phase_no_tank_heat.csv")
