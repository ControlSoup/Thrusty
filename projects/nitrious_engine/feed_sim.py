from gaslighter import (STD_ATM_K, STD_ATM_PA, DataStorage,
                        circle_area_from_diameter, convert, np_rk4)
from gaslighter.fluids import BasicStaticVolume, DryerOrifice, EquilibrumTank
from tqdm import tqdm

data: DataStorage = DataStorage.from_arange(start=0.0, end=10.0, dx=1e-3)


# -----------------------------------------------------------------------------
#  Nos
# -----------------------------------------------------------------------------

# Bottle = https://www.amazon.com/Bottle-Cold-Fusion-Nitrous-Fitting/dp/B0BT89VNB8/ref=sr_1_6?dib=eyJ2IjoiMSJ9.S5kZxR4TYzGcTXQlJzklIiG-J7Iwb4hJmMDZpY90DC7mPvNNJjsfsAJmPrLy59dGopQT8pgMt8xJbO5xEeTK70ND-_RMJxD2BpB9CHSpVM2enfr3niIfH00TzIfRqQ4eOnZDMEmhjQ7Oy2cttqHQMtbv6fprK2fh-4pvPP0FwRbdt5Lioep6KAjvRj8X4hsN4sf8_YAYqTI1tgpp2kE-LbfRsMx1sZyRwEEHwEPdw2kd2HbA8lgtH_L7ss2SPkam6JeRjyWzWuYYK8nU4YDNeuZDTSZi9JRJg692DGX67H8.wk39GuD1c4anAKBcBTOi7HhcbdcPm1Gwr5dBzsGuH24&dib_tag=se&keywords=nitrous+bottle&qid=1711325036&sr=8-6
nitrous_tank: EquilibrumTank = EquilibrumTank.from_mass(
    starting_pressure=convert(1000, "psia", "Pa"),
    mass=convert(35, "lbm", "kg"),
    fluid="N2O",
)
# No Injector
cd = 0.63  # <- need data
orifice_diameter_m = convert(11 / 64, "in", "m")
orifice: DryerOrifice = DryerOrifice(
    cd=cd, area=circle_area_from_diameter(orifice_diameter_m), fluid="N2O"
)

for t in tqdm(data.data_array):

    # Nitrious
    nitrous_mdot = orifice.mdot(
        nitrous_tank.pressure, nitrous_tank.temp, convert(150, "psia", "Pa")
    )
    try:
        nitrous_tank.integrate_state(nitrous_mdot, data.dx)
    except Exception:
        print(Exception)
        break

    # Stop if no flow
    if nitrous_tank.total_mass <= 0.0:
        break

    # Record Results
    data.record_from_dict(nitrous_tank.dict(prefix="nitrious_tank"))
    data.record_from_dict(orifice.dict(prefix="nitrious_orifice"))
    data.next_cycle()

data.plot_imperial(export_path="plots/feed_sim.html")
