from gaslighter import *
from gaslighter import fluids

# Setup ullage tank
# https://gascylindersource.com/shop/nitrogen-cylinders/40-cu-ft-steel-nitrogen-cylinder/
gas_state = fluids.IntensiveState(
    'P',  convert(2500, 'psia', 'Pa'), 
    'T', convert(80, 'degF', 'degK'), 
    'nitrogen'
)
gas_volume = convert(7.8, 'liters', 'm^3')
gas_mass = gas_volume * gas_state.density


# Calculate Mass Usage Through a Run

# Use the whole tank volume to be conservative 
usage_mass: fluids.BasicStaticVolume = fluids.BasicStaticVolume.from_ptv(
    convert(200, 'psia', 'Pa'),
    convert(80, 'degF', 'degK'),
    convert(5.9, 'liters', 'm^3'),
    'nitrogen'
).mass

print("____ Inital Pressurant Tank Parameters ____")
print(pretty_dict(imperial_dictionary({
    "Voume [m^3]": gas_volume,
    "Mass [kg]": gas_mass,
    "Pressure [Pa]": gas_state.pressure,
    "Temp [degK]": gas_state.temp,
})))

# Isentropic Reducantion in Mass
gas_state = gas_state.isentropic('D', (gas_mass - usage_mass) / gas_volume)

print("____ Isentropic Usage____")
print(pretty_dict(imperial_dictionary({
    "New Mass [kg]": gas_state.density * gas_volume,
    "New Pressure [Pa]": gas_state.pressure,
    "New Temp [degK]": gas_state.temp,
})))




