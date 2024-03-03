import unittest

from gaslighter import STD_ATM_PA, convert
from gaslighter.fluids import IncompressibleOrifice, IncompressiblePipe


class Test(unittest.TestCase):
    def test_incompressible_pipe(self):
        # Tests for fidelty are done on the functions
        # This test just looks to make sure results are repeatable

        PIPE_LENGTH_M = 100
        PIPE_D_M = 0.01
        RELATIVE_ROUGHNESS = 0.001

        pipe = IncompressiblePipe.from_relative_roughness(
            PIPE_D_M, RELATIVE_ROUGHNESS, PIPE_LENGTH_M, "water"
        )

        upstream_press = 1000 * STD_ATM_PA
        upstream_temp = 280

        dp_1 = pipe.dp(1e-1, upstream_press, upstream_temp)
        dp_2 = pipe.dp(1e-2, upstream_press, upstream_temp)
        dp_3 = pipe.dp(1e-3, upstream_press, upstream_temp)
        mdot_1 = pipe.mdot(upstream_press, upstream_temp, upstream_press - dp_1)
        mdot_2 = pipe.mdot(upstream_press, upstream_temp, upstream_press - dp_2)
        mdot_3 = pipe.mdot(upstream_press, upstream_temp, upstream_press - dp_3)

        self.assertAlmostEqual(mdot_1, 1e-1, delta=1e-5)
        self.assertAlmostEqual(mdot_2, 1e-2, delta=1e-5)
        self.assertAlmostEqual(mdot_3, 1e-3, delta=1e-5)

    def test_oirifce(self):
        # Tests for fidelty are done on the functions
        # This test just looks to make sure results are repeatable

        OR_D_M = 0.01

        orifice = IncompressibleOrifice.from_cda(cda=0.01, fluid="water")
        orifice2 = IncompressibleOrifice.from_cv(
            cv=convert(0.01, "m^2", "in^2") * 38, fluid="water"
        )

        self.assertAlmostEqual(orifice.cda, orifice2.cda)

        upstream_press = 1000 * STD_ATM_PA
        upstream_temp = 280

        dp_1 = orifice.dp(1, upstream_press, upstream_temp)
        dp_2 = orifice.dp(10, upstream_press, upstream_temp)
        dp_3 = orifice.dp(100, upstream_press, upstream_temp)

        mdot_1 = orifice.mdot(upstream_press, upstream_temp, upstream_press - dp_1)
        mdot_2 = orifice.mdot(upstream_press, upstream_temp, upstream_press - dp_2)
        mdot_3 = orifice.mdot(upstream_press, upstream_temp, upstream_press - dp_3)

        self.assertAlmostEqual(mdot_1, 1)
        self.assertAlmostEqual(mdot_2, 10)
        self.assertAlmostEqual(mdot_3, 100)


if __name__ == "__main__":
    unittest.main()
