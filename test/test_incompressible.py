import unittest

from gaslighter import *
from gaslighter.fluids import (IntensiveState, incompressible_orifice_dp,
                               incompressible_orifice_mdot)


class Test(unittest.TestCase):
    def test_incompressible_orifice(self):
        cv = 1
        cda = convert(cv, "Cv", "Cda_m2")
        upstrm_press_Pa = convert(100, "psia", "Pa")
        upstrm_temp_K = 280
        downstrm_press_Pa = STD_ATM_PA
        fluid = "water"

        upstream: IntensiveState = IntensiveState.from_pt(
            upstrm_press_Pa, upstrm_temp_K, fluid
        )

        mdot_kgps = incompressible_orifice_mdot(
            cda, upstream.pressure, upstream.density, downstrm_press_Pa
        )

        # Compare to Cv equation
        m3ps = convert(cv * np.sqrt(100 - STD_ATM_PSIA / 1), "gpm", "m^3/s")
        self.assertAlmostEqual(m3ps, mdot_kgps / upstream.density, delta=1e-6)

        # Ensure dp and flow and backward compatabile
        self.assertAlmostEqual(
            upstrm_press_Pa - downstrm_press_Pa,
            incompressible_orifice_dp(cda, upstream.density, mdot_kgps),
            delta=1e-8,
        )


if __name__ == "__main__":
    unittest.main()
