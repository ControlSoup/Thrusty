import unittest

from gaslighter import *
from gaslighter.fluids import (
    IntensiveState,
    friction_factor,
    incompressible_orifice_dp,
    incompressible_orifice_mdot,
    incompressible_pipe_dp,
    incompressible_orifice_cda,
)


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
        result_cda = incompressible_orifice_cda(
            mdot_kgps, upstream.pressure, upstream.density, downstrm_press_Pa
        )

        # Compare to Cv equation
        m3ps = convert(cv * np.sqrt(100 - STD_ATM_PSIA / 1), "gpm", "m^3/s")
        self.assertAlmostEqual(m3ps, mdot_kgps / upstream.density, delta=1e-6)
        self.assertAlmostEqual(cda, result_cda, delta=1e-6)

        # Ensure dp and flow and backward compatabile
        self.assertAlmostEqual(
            upstrm_press_Pa - downstrm_press_Pa,
            incompressible_orifice_dp(cda, upstream.density, mdot_kgps),
            delta=1e-8,
        )

    def test_incompressible_pipe(self):
        # https://www.omnicalculator.com/physics/darcy-weisbach

        PIPE_LENGTH_M = 1
        PIPE_D_M = 0.01
        FLOW_VELOCITY_MPS = 1
        DENSITY_KGPM3 = 1000
        DARCY_FF = 0.01

        DP_PA = incompressible_pipe_dp(
            length=PIPE_LENGTH_M,
            hydraulic_diameter=PIPE_D_M,
            density=DENSITY_KGPM3,
            flow_velocity=FLOW_VELOCITY_MPS,
            friciton_factor=DARCY_FF,
        )

        # Check pipe dp
        self.assertAlmostEqual(DP_PA, 500)

        # https://www.omnicalculator.com/physics/friction-factor
        ff = friction_factor(reynolds=4500, relative_roughness=0.001)
        self.assertAlmostEqual(ff, 0.039785, delta=1e-2)


if __name__ == "__main__":
    unittest.main()
