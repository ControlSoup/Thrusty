import unittest

from gaslighter import *
from gaslighter.fluids import IntensiveState, real_orifice_mdot


class Test(unittest.TestCase):
    def test_ideal_orifice(self):
        Cd = 0.5
        orifice_area_m2 = 0.05
        upstrm_press_Pa = 300000
        upstrm_temp_K = 320
        downstrm_press_Pa = 101000
        fluid = "nitrogen"

        upstream: IntensiveState = IntensiveState.from_pt(
            upstrm_press_Pa, upstrm_temp_K, fluid
        )

        # Calc mdot with information on if its choked or not
        mdot_kgps, is_choked = real_orifice_mdot(
            Cd * orifice_area_m2, upstream, downstrm_press_Pa, verbose_return=True
        )

        # Test if choked
        self.assertTrue(is_choked)

        self.assertAlmostEqual(mdot_kgps, 16.679131378034153, delta=1e-2)


if __name__ == "__main__":
    unittest.main()
