"""Small equation checks. Run with python -m unittest -v test_numerics.

These check the implemented algebra, not convergence for every Richards problem.
The complete reproduction is performed by reproduce.py.
"""
import unittest
from dataclasses import replace
import numpy as np
import richards_revised as R


def dense(ab):
    return np.diag(ab[1]) + np.diag(ab[0, 1:], 1) + np.diag(ab[2, :-1], -1)


class NumericalChecks(unittest.TestCase):
    def test_capacity_is_retention_derivative_in_unsaturated_soil(self):
        for name in ("warrick", "polmann", "miller", "lehmann"):
            s = R.make_case(name).soil
            h = -np.array([.1, 1, 10]) / s.alpha
            delta = 1e-5 * np.abs(h)
            numeric = (s.theta(h + delta) - s.theta(h - delta)) / (2 * delta)
            np.testing.assert_allclose(s.C(h), numeric, rtol=2e-7, atol=1e-11)

    def test_capacity_maximum(self):
        for name in ("warrick", "polmann", "miller", "lehmann"):
            s = R.make_case(name).soil
            h = -np.logspace(-6, 6, 10001) / s.alpha
            self.assertGreaterEqual(s.cmax(), np.max(s.C(h)) * (1 - 1e-12))
            self.assertLess(s.cmax() / np.max(s.C(h)), 1.0001)

    def test_complete_newton_jacobian(self):
        for name, dz, dt in (("polmann", 20., 100.), ("lehmann", 30., .1)):
            c = replace(R.make_case(name), dz=dz)
            h = -np.linspace(2, 20, len(c.z())) / c.soil.alpha
            old = h * 1.1
            qt = c.qtop(0)
            for form in ("mixed", "psi"):
                _, _, dl, du = R.residual(c, form, h, old, dt, qt, True)
                cap = c.soil.C(h) if form == "mixed" else c.soil.Cp(h) + c.soil.dCp(h) * (h-old)
                J = dense(R.banded(c.dz * cap / dt, dl, du))
                Jfd = np.empty_like(J)
                for j in range(len(h)):
                    eps = 1e-5 * max(1, abs(h[j]))
                    p, m = h.copy(), h.copy()
                    p[j] += eps
                    m[j] -= eps
                    Jfd[:, j] = (R.residual(c, form, p, old, dt, qt)[0] -
                                  R.residual(c, form, m, old, dt, qt)[0]) / (2*eps)
                np.testing.assert_allclose(J, Jfd, rtol=1e-5, atol=1e-12)

    def test_l_iteration_solves_stabilised_mixed_equation(self):
        c = replace(R.make_case("polmann"), dz=20.)
        old = c.psi0(c.z())
        L, dt = c.soil.cmax(), 100.
        opts = dict(tolF=1e100, tolH=1e100, maxit=1, L=L)
        h, it, _, _ = R.step(c, "lscheme", old, dt, None, opts)
        q, _, _ = R.faces(c, h, c.soil.K(old))
        balance = c.dz * L * (h-old) / dt + np.diff(q)
        np.testing.assert_allclose(balance, 0, atol=1e-12)
        self.assertEqual(it, 1)

    def test_flux_divergence_telescopes(self):
        c = replace(R.make_case("lehmann"), dz=30.)
        h = -np.linspace(10., 1000., len(c.z()))
        old, dt = h * 1.2, .1
        F, q, _, _ = R.residual(c, "mixed", h, old, dt, c.qtop(0))
        storage = c.dz * np.sum(c.soil.theta(h) - c.soil.theta(old))
        np.testing.assert_allclose(dt * np.sum(F), storage - dt * (q[0]-q[-1]), rtol=1e-13, atol=1e-13)

    def test_picard_newton_and_hybrid_agree_at_convergence(self):
        c = replace(R.make_case("polmann"), dz=5., duration=900.)
        results = [R.run(c, method, 900., wall_limit=float("inf")) for method in
                   ("modpicard", "newton_mixed", "lnewton")]
        for r in results:
            self.assertEqual(r["status"], "completed")
            self.assertLess(abs(r["epsB"]), 1e-6)
            np.testing.assert_allclose(r["theta"], results[0]["theta"], rtol=1e-7, atol=1e-8)


if __name__ == "__main__":
    unittest.main()
