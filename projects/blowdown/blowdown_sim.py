from thrusty import *
from thrusty import fluids

data = DataStorage(
    1e-3,
    100.0
)

tank: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    pressure = convert(1000.0, 'psia', 'Pa'),
    temp = STD_ATM_K,
    volume = convert(1, 'gal', 'm^3'),
    fluid = "air"
)