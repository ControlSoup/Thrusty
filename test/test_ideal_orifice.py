import unittest
from thrusty.fluids.ideal_gas import *
from thrusty.fluids import IntensiveState

class Test(unittest.TestCase):
    def test_ideal_orifice(self):
        Cd = 0.5
        orifice_area_m2 = 0.05
        upstrm_press_Pa = 300000
        upstrm_temp_K = 320
        downstrm_press_Pa = 101000
        fluid = 'nitrogen'

        upstream: IntensiveState = IntensiveState.from_pt(
            upstrm_press_Pa,
            upstrm_temp_K,
            fluid
        )
        print(upstream.__dict__)

        # Ensure inputs are choked
        self.assertTrue(
            ideal_is_choked(
                upstream.pressure,
                upstream.gamma,
                downstrm_press_Pa
            )
        )


        mdot_kgps = ideal_orifice_mdot(
            Cd * orifice_area_m2,
            upstream,
            downstrm_press_Pa
        )

        self.assertAlmostEqual(
            mdot_kgps,
            16.679131378034153,
            delta=1e-4
        )
        print("YA")

if __name__ == "__main__":
    unittest.main()