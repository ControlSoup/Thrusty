import numpy as np

def np_within_tolerance(array: np.array, target: float, tolerance: float = 1e-4):
  # Find the indices where the absolute difference between the array values and the target is within the tolerance
    within_tolerance_indices = np.where(np.abs(array - target) <= tolerance)[0]

    # If there are any indices found, return the first one; otherwise, return None
    if within_tolerance_indices.size > 0:
        return within_tolerance_indices[0]
    else:
        raise ValueError(f"Could not find value [{target}] within tolerance [{tolerance}]")

def np_poly(x: np.array, y: np.array, degree: int):
    polyfit = np.polyfit(x, y, degree)
    return np.poly1d(polyfit)