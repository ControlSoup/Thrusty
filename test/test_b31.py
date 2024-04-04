import unittest

from gaslighter.asme import b313
from gaslighter.fluids import IntensiveState
from gaslighter.fluids.ideal_gas import *


class Test(unittest.TestCase):
    def test_b31(self):
        # https://www.engineeringtoolbox.com/asme-31.3-piping-pressure-calculations-d_2158.html
        thickness = 0.237
        od = 4.5
        thickness_tolerance = 12.5
        allowable = 16000
        quality = 0.8
        thermal_coef = 0.4

        pressure = b313.pipe_pressure(
            thickness=thickness,
            outside_diameter=od,
            allowable_tensile=allowable,
            quality_factor=quality,
            thermal_coefficent=thermal_coef,
            thickness_percent_tolerance=thickness_tolerance,
        )

        self.assertAlmostEqual(1232, pressure, delta=4)


if __name__ == "__main__":
    unittest.main()
