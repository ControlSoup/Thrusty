import numpy as np

from .. import circle_area_from_diameter
from . import spad, sutton


class RocketEngineGeometry:
    def __init__(
        self,
        chamber_diameter: float,
        chamber_length: float,
        chamber_volume: float,
        exit_diameter: float,
        exit_length: float,
        throat_diameter: float,
    ):
        """
        Geometry holder engines

        NOTE: No internal class parameters are intentded for extenral modification
        TODO: Add contration ratio losses?
        """

        self.chamber_area = circle_area_from_diameter(chamber_diameter)
        self.chamber_diameter = chamber_diameter
        self.chamber_length = chamber_length
        self.chamber_volume = chamber_volume

        self.exit_area = circle_area_from_diameter(exit_diameter)
        self.exit_diameter = exit_diameter
        self.exit_length = exit_length

        self.throat_area = circle_area_from_diameter(throat_diameter)
        self.throat_diameter = throat_diameter

        self.lstar = sutton.lstar(self.chamber_volume, self.throat_area)
        self.contration_ratio = self.chamber_area / self.throat_area
        self.expansion_ratio = sutton.eps(self.exit_area, self.throat_area)
        self.exit_half_angle = sutton.half_angle_rad(
            self.throat_diameter, self.exit_length, self.exit_diameter
        )
        self.half_angle_losses = spad.half_angle_losses(self.exit_half_angle)

    def dict(self, prefix: str = None):
        if prefix is None:
            prefix = ""
        else:
            prefix = f"{prefix}."
        return {
            f"{prefix}Chamber Area [m^2]": self.chamber_area,
            f"{prefix}Chamber Diameter [m]": self.chamber_diameter,
            f"{prefix}Chamber Length [m]": self.chamber_length,
            f"{prefix}Chamber Volume [m^3]": self.chamber_volume,
            f"{prefix}Contraction Ratio [-]": self.contration_ratio,
            f"{prefix}Exit Area [m^2]": self.exit_area,
            f"{prefix}Exit Diameter [m]": self.exit_diameter,
            f"{prefix}Exit Half Angle [rad]": self.exit_half_angle,
            f"{prefix}Exit Length [m]": self.exit_length,
            f"{prefix}Expansion Ratio [-]": self.expansion_ratio,
            f"{prefix}Half Angle Losses [-]": self.half_angle_losses,
            f"{prefix}Lstar [m]": self.lstar,
            f"{prefix}Throat Area [m^2]": self.throat_area,
            f"{prefix}Throat Diameter [m]": self.throat_diameter,
        }
