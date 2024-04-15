"""
Source: 
https://en.wikipedia.org/wiki/Cylinder_stress
"""

def thin_wall_hoop_stress(
    pressure: float, 
    radius: float, 
    thickness: float, 
    suppress_warning: bool = False
):
    if not suppress_warning:
        if radius * 2 / thickness <= 20.0:
            print(
                f"WARNING| Thin Wall Assumption has been violated with D/t = {radius * 2 / thickness}"
            )

    return pressure * radius / thickness


def thin_wall_hoop_pressure(
    stress: float, 
    radius: float, 
    thickness: float, 
    suppress_warning: bool = False
):
    if not suppress_warning:
        if radius * 2 / thickness <= 20.0:
            print(
                f"WARNING| Thin Wall Assumption has been violated with D/t = {radius * 2 / thickness}"
            )

    return stress * thickness / radius
