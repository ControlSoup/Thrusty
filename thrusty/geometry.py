import numpy as np

def circle_area_from_diameter(diamter: float):
    return np.pi * diamter**2 / 4.0

def circle_area_from_radius(radius: float):
    return np.pi * radius**2

def circle_diameter_from_area(area: float):
    return np.sqrt((4.0 * area) / np.pi)

def circle_radius_from_area(area:float):
    return np.sqrt(area / np.pi)