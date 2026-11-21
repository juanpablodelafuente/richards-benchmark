"""Revised common framework for the five 1-D Richards' equation benchmarks.

Replaces the per-benchmark notebooks of juanpablodelafuente/richards-benchmark (commit 222c73a)
for the revised manuscript. Corrections with respect to the notebooks:
  1. Newton uses the complete Jacobian (theta or C and K re-evaluated at the perturbed state,
     analytic tridiagonal assembly with nodal finite-difference derivatives of K and C).
     The notebooks held C and K fixed, which reproduced the Picard matrix.
  2. Every iterative step must satisfy BOTH a scaled residual test and a head-increment test.
     A step that reaches the iteration limit is a failure: the run stops and is reported as
     failed. The notebooks accepted the last iterate silently.
  3. Mass balance uses the fluxes of each scheme's own update (old-level conductivity for the
     linearly implicit scheme, old state for the explicit scheme, converged state otherwise).
  4. All tridiagonal systems are solved with a banded solver (the notebooks used dense solves).
  5. One grid, boundary treatment and interface rule (arithmetic mean) for every scheme.
     Warrick uses unit-gradient drainage at the base for all schemes, as in Warrick (2003)
     and in the explicit notebook (the implicit notebook used a fixed head).
  6. Miller uses m = 1 - 1/n exactly (the K expression assumes this identity).
  7. Daily flux forcing can be sub-stepped (flux constant within each day), needed for
     refined references of the Lehmann and Ireson benchmarks.
Upward coordinate z, upward-positive Darcy flux q = -K (dpsi/dz + 1).
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
import numpy as np
from scipy.linalg import solve_banded

LEHMANN_RAIN = np.array([
    0, 1, .6, .8, .5, .1, .3, .6, .7, .4, -.1, -.05, -.1, -.15, -.05,
    -.14, -.05, 0, -.05, -.07, -.05, -.04, -.01, -.03, -.005, -.03,
    -.04, -.02, -.01, -.005, 0, 0, 0, 0, .8, 1.5, .5, .7, -.18,
    -.16, -.05, -.05, -.1, -.04, -.02, -.005, -.01, -.005, -.005,
    -.05, -.1, 0, 0, 0, 0, 0, 0, .8, 1.4, 1.2], dtype=float)   # cm/day, + infiltration


@dataclass(frozen=True)
class Soil:
    theta_r: float
    theta_s: float
    alpha: float
    n: float
    ks: float
    m: float | None = None          # None -> 1 - 1/n
    ss: float = 1e-6                # Picard-type capacity used where psi >= 0 (notebook convention)

    @property
    def mm(self):
        return 1 - 1 / self.n if self.m is None else self.m

    def theta(self, h):
        h = np.asarray(h, float)
        x = self.alpha * np.maximum(-h, 0.0)
        return self.theta_r + (self.theta_s - self.theta_r) * (1 + x ** self.n) ** (-self.mm)

    def C(self, h):                 # true d theta / d psi (zero at and above saturation)
        h = np.asarray(h, float)
        x = self.alpha * np.maximum(-h, 0.0)
        m, n = self.mm, self.n
        c = (self.theta_s - self.theta_r) * self.alpha * n * m * x ** (n - 1) / (1 + x ** n) ** (m + 1)
        return np.where(h < 0, c, 0.0)

    def Cp(self, h):                # capacity used by the pressure-head and Picard-type schemes
        h = np.asarray(h, float)
        return np.where(h < 0, self.C(h), self.ss)

    def K(self, h):
        h = np.asarray(h, float)
        x = self.alpha * np.maximum(-h, 0.0)
        m, n = self.mm, self.n
        a = 1 + x ** n
        k = self.ks * (1 - x ** (n - 1) * a ** (-m)) ** 2 / a ** (0.5 * m)
        return np.where(h >= 0, self.ks, k)

    def _d(self, f, h):
        h = np.asarray(h, float)
        e = 1e-7 * np.maximum(1.0, np.abs(h))
        return (f(h + e) - f(h - e)) / (2 * e)

    def dK(self, h):
        return self._d(self.K, h)

    def dCp(self, h):
        return self._d(self.Cp, h)

    def psi_of_theta(self, th):     # inverse retention (explicit scheme); NaN below theta_r
        se = (np.asarray(th, float) - self.theta_r) / (self.theta_s - self.theta_r)
        with np.errstate(invalid='ignore', divide='ignore'):
            h = -((se ** (-1 / self.mm) - 1) ** (1 / self.n)) / self.alpha
        return np.where(se >= 1, 0.0, np.where(se > 0, h, np.nan))

    def cmax(self):
        m, n = self.mm, self.n
        x = ((n - 1) / (n * m + 1)) ** (1 / n)
        return float((self.theta_s - self.theta_r) * self.alpha * n * m * x ** (n - 1) / (1 + x ** n) ** (m + 1))


@dataclass
class Case:
    name: str
    soil: Soil
    H: float
    dz: float
    grid: str                       # 'vertex' (head-type top) or 'cell' (flux top)
    duration: float
    length_unit: str
    time_unit: str
    psi0: callable
    top_head: float | None = None
    bottom_head: float | None = None   # None -> unit-gradient (free) drainage
    flux: np.ndarray | None = None     # upward-positive flux per forcing interval, index 1..
    day: float = 1.0

    def z(self):
        E = int(round(self.H / self.dz))
        assert abs(E * self.dz - self.H) < 1e-9 * self.H
        if self.grid == 'vertex':
            return np.arange(1, E) * self.dz
        return (np.arange(E) + 0.5) * self.dz

    def qtop(self, t):
        if self.flux is None:
            return None
        return float(self.flux[int(np.floor(t / self.day + 1e-9)) + 1])


def make_case(name, data_dir=Path(__file__).resolve().parent.parent / 'notebooks' / 'ireson'):
    if name == 'warrick':
        return Case('warrick', Soil(.124, .495, .015, 2., 1.23e-5), 125., 5., 'vertex', 360000., 'cm', 's',
                    lambda z: np.full(z.size, -202.528116), top_head=0.0, bottom_head=None)
    if name == 'polmann':
        return Case('polmann', Soil(.102, .368, .0335, 2., .00922), 100., 2.5, 'vertex', 21600., 'cm', 's',
                    lambda z: np.full(z.size, -1000.), top_head=-75., bottom_head=-1000.)
    if name == 'miller':
        return Case('miller', Soil(.093, .301, 5.470, 4.264, 5.040), 10., .0125, 'vertex', .18, 'm', 'day',
                    lambda z: -z, top_head=0.1, bottom_head=0.0)
    if name == 'lehmann':
        return Case('lehmann', Soil(.1060, .4686, .0104, 1.3954, 13.1), 180., 2., 'cell', 59., 'cm', 'day',
                    lambda z: np.full(z.size, -10000.), flux=-LEHMANN_RAIN)
    if name == 'ireson':
        p = np.loadtxt(Path(data_dir) / 'infiltration.dat', delimiter=',', skiprows=1, usecols=1) / 1000.
        return Case('ireson', Soil(.131, .396, .423, 2.06, .0496), 1.5, .05, 'cell', float(len(p) - 1), 'm', 'day',
                    lambda z: np.full(z.size, -3.59), flux=-p)
    raise ValueError(name)


# ----------------------------------------------------------------------------------------------
def faces(case, h, K, dK=None, qtop=None):
    """Face fluxes q[0..N] (bottom to top) and their derivatives w.r.t. the node below (dl)
    and above (du). Nodal K is passed separately so that lagged schemes can use old K."""
    s, dz, N = case.soil, case.dz, len(h)
    q, dl, du = np.empty(N + 1), np.zeros(N + 1), np.zeros(N + 1)
    Kf = 0.5 * (K[:-1] + K[1:])
    g = (h[1:] - h[:-1]) / dz + 1
    q[1:-1] = -Kf * g
    dl[1:-1] = Kf / dz
    du[1:-1] = -Kf / dz
    if dK is not None:
        dl[1:-1] -= 0.5 * dK[:-1] * g
        du[1:-1] -= 0.5 * dK[1:] * g
    if case.bottom_head is not None:
        Kb = 0.5 * (float(s.K(case.bottom_head)) + K[0])
        gb = (h[0] - case.bottom_head) / dz + 1
        q[0] = -Kb * gb
        du[0] = -Kb / dz - (0.5 * dK[0] * gb if dK is not None else 0.0)
    else:                                   # unit-gradient drainage
        q[0] = -K[0]
        du[0] = -dK[0] if dK is not None else 0.0
    if case.top_head is not None:
        Kt = 0.5 * (K[-1] + float(s.K(case.top_head)))
        gt = (case.top_head - h[-1]) / dz + 1
        q[-1] = -Kt * gt
        dl[-1] = Kt / dz - (0.5 * dK[-1] * gt if dK is not None else 0.0)
    else:
        q[-1] = qtop
    return q, dl, du


def banded(dS, dl, du):
    ab = np.zeros((3, dS.size))
    ab[1] = dS + dl[1:] - du[:-1]
    ab[0, 1:] = du[1:-1]
    ab[2, :-1] = -dl[1:-1]
    return ab


MIXED = {'modpicard', 'newton_mixed', 'lscheme', 'lnewton'}


def residual(case, form, h, hold, dt, qtop, need_dK=False):
    s, dz = case.soil, case.dz
    K = s.K(h)
    dK = s.dK(h) if need_dK else None
    q, dl, du = faces(case, h, K, dK, qtop)
    if form == 'mixed':
        F = dz * (s.theta(h) - s.theta(hold)) / dt + np.diff(q)
    else:
        F = dz * s.Cp(h) * (h - hold) / dt + np.diff(q)
    return F, q, dl, du


class StepFailure(Exception):
    pass


def step(case, method, hold, dt, qtop, opt):
    """One time step. Returns new head, iterations, MB fluxes (scheme-consistent), end-state fluxes."""
    s, dz = case.soil, case.dz
    if method == 'linimp':                       # one solve with C, K at the old level
        Kold = s.K(hold)
        q0, dl, du = faces(case, hold, Kold, None, qtop)
        ab = banded(dz * s.Cp(hold) / dt, dl, du)
        hnew = hold + solve_banded((1, 1), ab, -np.diff(q0), check_finite=False)
        if not np.all(np.isfinite(hnew)):
            raise StepFailure('non-finite solution')
        q_mb, _, _ = faces(case, hnew, Kold, None, qtop)
        q_end, _, _ = faces(case, hnew, s.K(hnew), None, qtop)
        return hnew, 1, q_mb, q_end
    form = 'mixed' if method in MIXED else 'psi'
    tolF, tolH, maxit = opt['tolF'], opt['tolH'], opt['maxit']
    L = opt.get('L') or s.cmax()
    h = hold.copy()
    for it in range(1, maxit + 1):
        newton = method in ('newton_psi', 'newton_mixed') or (method == 'lnewton' and it > opt.get('nL', 5))
        F, q, dl, du = residual(case, form, h, hold, dt, qtop, need_dK=newton)
        if method == 'lscheme' or (method == 'lnewton' and not newton):
            dS = np.full(h.size, dz * L / dt)
        elif method == 'newton_mixed' or (method == 'lnewton' and newton):
            dS = dz * s.C(h) / dt
        elif method == 'newton_psi':
            dS = dz * (s.Cp(h) + s.dCp(h) * (h - hold)) / dt
        else:                                     # picard_psi, modpicard
            dS = dz * s.Cp(h) / dt
        try:
            d = solve_banded((1, 1), banded(dS, dl, du), -F, check_finite=False)
        except (np.linalg.LinAlgError, ValueError) as exc:
            raise StepFailure(f'singular linear system at iteration {it}') from exc
        if not np.all(np.isfinite(d)):
            raise StepFailure(f'non-finite update at iteration {it}')
        lam = 1.0
        if newton and opt.get('linesearch', False):
            f0 = np.max(np.abs(F))
            while lam > 1 / 256:
                Ft = residual(case, form, h + lam * d, hold, dt, qtop)[0]
                if np.max(np.abs(Ft)) <= (1 - 1e-4 * lam) * f0:
                    break
                lam *= 0.5
        h = h + lam * d
        Fn, qn, _, _ = residual(case, form, h, hold, dt, qtop)
        if (np.max(np.abs(Fn)) * dt / dz <= tolF and
                lam * np.max(np.abs(d)) <= tolH * max(1.0, np.max(np.abs(h)))):
            return h, it, qn, qn
    raise StepFailure(f'no convergence in {maxit} iterations (scaled residual {np.max(np.abs(Fn)) * dt / dz:.2e})')


def explicit_step(case, th, dt, qtop):
    s = case.soil
    h = s.psi_of_theta(th)
    if not np.all(np.isfinite(h)):
        raise StepFailure('water content left the admissible range (theta < theta_r)')
    q, _, _ = faces(case, h, s.K(h), None, qtop)
    thn = th - dt / case.dz * np.diff(q)
    if not np.all(np.isfinite(thn)):
        raise StepFailure('non-finite water content')
    return thn, q


def schedule(case, dt):
    if case.flux is not None:
        k = int(round(case.day / dt))
        assert abs(k * dt - case.day) < 1e-9, 'dt must divide the forcing interval'
        n_int = int(round(case.duration / case.day))
        for j in range(n_int):
            for i in range(k):
                yield j * case.day + i * dt, dt, (i == k - 1)
    else:
        t = 0.0
        while t < case.duration - 1e-9 * case.duration:
            h = min(dt, case.duration - t)
            yield t, h, False
            t += h


def run(case, method, dt, tolF=1e-9, tolH=1e-8, maxit=10000, L=None, nL=5, linesearch=None,
        adapt=False, wall_limit=900.0):
    """Run one simulation. adapt=True (references only) halves a failed step recursively."""
    s, z = case.soil, case.z()
    opt = dict(tolF=tolF, tolH=tolH, maxit=maxit, L=L, nL=nL,
               linesearch=(method == 'lnewton') if linesearch is None else linesearch)
    h = case.psi0(z).astype(float)
    th = s.theta(h)
    S0 = case.dz * th.sum()
    S, Q, Qend, its = S0, 0.0, 0.0, []
    daily_S, status, reason = [S0], 'completed', ''
    t_end = 0.0
    tic = time.perf_counter()

    def advance(hc, thc, t, dtt, depth=0):
        qt = case.qtop(t)
        if method == 'explicit':
            thn, q = explicit_step(case, thc, dtt, qt)
            return s.psi_of_theta(thn), thn, 1, q, q
        try:
            hn, n_it, q_mb, q_end = step(case, method, hc, dtt, qt, opt)
            return hn, s.theta(hn), n_it, q_mb, q_end
        except StepFailure:
            if not adapt or depth > 12:
                raise
            h1, th1, n1, qa, qa_e = advance(hc, thc, t, dtt / 2, depth + 1)
            h2, th2, n2, qb, qb_e = advance(h1, th1, t + dtt / 2, dtt / 2, depth + 1)
            return h2, th2, n1 + n2, 0.5 * (qa + qb), 0.5 * (qa_e + qb_e)

    try:
        for t, dtt, end_of_day in schedule(case, dt):
            if time.perf_counter() - tic > wall_limit:
                status, reason = 'budget', f'wall-clock limit {wall_limit:.0f} s reached at t = {t:g}'
                break
            h, th, n_it, q_mb, q_end = advance(h, th, t, dtt)
            its.append(n_it)
            Q += dtt * (q_mb[0] - q_mb[-1])
            Qend += dtt * (q_end[0] - q_end[-1])
            t_end = t + dtt
            if end_of_day:
                daily_S.append(case.dz * th.sum())
    except StepFailure as exc:
        status, reason = 'failed', f'{exc} at t = {t:g} {case.time_unit} (step {len(its) + 1})'
    runtime = time.perf_counter() - tic
    S1 = case.dz * th.sum()
    its = np.array(its) if its else np.array([0])
    return dict(case=case.name, method=method, dz=case.dz, dt=dt, status=status, reason=reason,
                t_end=t_end, z=z, psi=h, theta=th, runtime=runtime,
                it_total=int(its.sum()), it_mean=float(its.mean()), it_max=int(its.max()), n_steps=int(len(its)),
                dS=S1 - S0, Qnet=Q, MB=(S1 - S0) / Q if Q != 0 else np.nan, epsB=Q - (S1 - S0),
                MB_endstep=(S1 - S0) / Qend if Qend != 0 else np.nan,
                daily_S=np.array(daily_S), length_unit=case.length_unit, time_unit=case.time_unit)


# ----------------------------------------------------------------------------------------------
def front_depth(case, z, th):
    """Depth below the surface at which theta first falls below the midpoint between the
    surface value and the initial value (head-boundary benchmarks)."""
    s = case.soil
    th_top = float(s.theta(case.top_head))
    mid = 0.5 * (th_top + s.theta(case.psi0(z)))
    depth = case.H - z
    order = np.argsort(depth)
    d, f = depth[order], (th - mid)[order]
    for i in range(1, len(d)):
        if f[i - 1] >= 0 > f[i]:
            return float(d[i - 1] + (d[i] - d[i - 1]) * f[i - 1] / (f[i - 1] - f[i]))
    return float('nan')


def errors(case, res, ref):
    """Reference errors (Eqs. E1-E2) at the run's nodes; reference interpolated linearly
    (exact node coincidence for integer refinement of vertex grids)."""
    s = case.soil
    pr = np.interp(res['z'], ref['z'], ref['psi'])
    tr = np.interp(res['z'], ref['z'], ref['theta'])
    e, et = res['psi'] - pr, res['theta'] - tr
    H = case.H
    out = dict(psi_rmse=float(np.sqrt(np.sum(case.dz * e ** 2) / H)), psi_max=float(np.max(np.abs(e))),
               theta_rmse=float(np.sqrt(np.sum(case.dz * et ** 2) / H)), theta_max=float(np.max(np.abs(et))))
    if case.top_head is not None:
        out['front'] = front_depth(case, res['z'], res['theta'])
        out['front_ref'] = front_depth(case, ref['z'], ref['theta'])
        out['front_err'] = out['front'] - out['front_ref']
    return out
