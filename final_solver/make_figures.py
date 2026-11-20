"""Regenerate the manuscript figures with reference solutions (run after run_all.py)."""
import json
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import richards_revised as R
from run_all import load, tag, hydrus_storage, OUT

FIG = Path(__file__).resolve().parent / 'figures'; FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': .3, 'legend.fontsize': 7.5,
                     'figure.dpi': 110, 'savefig.dpi': 220, 'savefig.bbox': 'tight'})
COL = {'explicit': '#8c564b', 'linimp': '#ff7f0e', 'picard_psi': '#1f77b4', 'newton_psi': '#1f77b4',
       'modpicard': '#2ca02c', 'newton_mixed': '#2ca02c', 'lscheme': '#d62728', 'lnewton': '#9467bd'}
LAB = {'explicit': 'Explicit', 'linimp': 'Implicit non-iterative', 'picard_psi': 'Picard (ψ-based)', 'newton_psi': 'Newton (ψ-based)',
       'modpicard': 'Picard (mixed)', 'newton_mixed': 'Newton (mixed)', 'lscheme': 'L-scheme (mixed)',
       'lnewton': 'L/Newton (mixed)'}
SHADES = ['#444444', '#1b9e77', '#d95f02', '#7570b3', '#e7298a']


def get(case, m, dz, dt):
    try:
        r = load(case, tag(m, dz, dt))
    except FileNotFoundError:
        return None
    return r if r['status'] == 'completed' else None


def prof(case, r, depth=True):
    c = R.make_case(case)
    z, p = np.asarray(r['z']), np.asarray(r['psi'])
    if c.bottom_head is not None:
        z, p = np.r_[0.0, z], np.r_[c.bottom_head, p]
    if c.top_head is not None:
        z, p = np.r_[z, c.H], np.r_[p, c.top_head]
    return (c.H - z if depth else z), p


def refline(ax, case, depth=True, swap=False, **kw):
    x, p = prof(case, load(case, 'ref1'), depth)
    a, b = (p, x) if swap else (x, p)
    ax.plot(a, b, color='k', lw=2.2, alpha=.85, label='Reference', zorder=1, **kw)


def lines(ax, case, specs, swap=False, depth=True):
    for k, (m, dz, dt, lab) in enumerate(specs):
        r = get(case, m, dz, dt)
        if r is None:
            continue
        x, p = prof(case, r, depth)
        a, b = (p, x) if swap else (x, p)
        ax.plot(a, b, color=SHADES[(k + 1) % len(SHADES)], lw=1.3, label=lab, zorder=3)


# ---------------- Fig. 2 hydraulic functions of the five soils (cm units) --------------------
def fig2():
    soils = {'Warrick': (R.Soil(.124, .495, .015, 2., 1.), (0, 202.5)),
             'Polmann': (R.Soil(.102, .368, .0335, 2., 1.), (75, 1000)),
             'Miller': (R.Soil(.093, .301, .0547, 4.264, 1.), (0.1, 1000)),
             'Lehmann': (R.Soil(.1060, .4686, .0104, 1.3954, 1.), (0.1, 10000)),
             'Ireson': (R.Soil(.131, .396, .00423, 2.06, 1.), (0.1, 359))}
    s_ = np.logspace(-1, 5, 400)
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.4))
    for k, (name, (s, rng)) in enumerate(soils.items()):
        c = f'C{k}'
        ax[0].semilogx(s_, s.theta(-s_), c, label=name)
        ax[1].loglog(s_, s.K(-s_), c)
        ax[2].loglog(s_, s.C(-s_), c)
        for a in ax:
            a.axvspan(max(rng[0], .1), rng[1], color=c, alpha=.06)
    ax[0].set(xlabel='Suction −ψ (cm)', ylabel='θ (−)', title='(a) Water retention')
    ax[1].set(xlabel='Suction −ψ (cm)', ylabel='K/K$_s$ (−)', title='(b) Relative conductivity', ylim=(1e-14, 2))
    ax[2].set(xlabel='Suction −ψ (cm)', ylabel='C = dθ/dψ (cm$^{-1}$)', title='(c) Moisture capacity', ylim=(1e-9, 3e-2))
    ax[0].legend()
    fig.tight_layout(); fig.savefig(FIG / 'Fig02_hydraulic_functions.png'); plt.close(fig)


def fig3():
    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    v = R.LEHMANN_RAIN[1:]
    ax.bar(np.arange(1, 60), v, color=np.where(v >= 0, '#1f77b4', '#d62728'), width=.8)
    ax.axhline(0, color='k', lw=.6)
    ax.set(xlabel='Day', ylabel='Surface flux (cm day$^{-1}$)', title='Positive: infiltration; negative: evaporation')
    fig.tight_layout(); fig.savefig(FIG / 'Fig03_lehmann_flux.png'); plt.close(fig)


def fig4():
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    lines(ax[0], 'warrick', [('explicit', 5., dt, f'Δt = {dt} s') for dt in (1, 300, 900, 1800)])
    lines(ax[1], 'warrick', [('linimp', 5., dt, f'Δt = {dt} s') for dt in (1, 900, 2400)])
    for a, t in zip(ax, ['(a) Explicit (mixed form)', '(b) Implicit non-iterative (ψ-based)']):
        refline(a, 'warrick'); a.set(xlabel='Depth (cm)', title=t, xlim=(0, 125)); a.legend()
    ax[0].set_ylabel('Pressure head (cm)')
    fig.tight_layout(); fig.savefig(FIG / 'Fig04_warrick.png'); plt.close(fig)


def fig5():
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    lines(ax[0], 'polmann', [('explicit', 2.5, dt, f'Δt = {dt} s') for dt in (1, 42)])
    lines(ax[1], 'polmann', [('linimp', 2.5, dt, f'Δt = {dt} s') for dt in (1, 270, 900, 3000, 5400)])
    for a, t in zip(ax, ['(a) Explicit (fails for Δt ≥ 50 s)', '(b) Implicit non-iterative (ψ-based)']):
        refline(a, 'polmann'); a.set(xlabel='Depth (cm)', title=t, xlim=(0, 100)); a.legend(loc='lower right')
    ax[0].set_ylabel('Pressure head (cm)')
    fig.tight_layout(); fig.savefig(FIG / 'Fig05_polmann_noniterative.png'); plt.close(fig)


def fig6():
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for a, (mp, mn), t in zip(ax, [('picard_psi', 'newton_psi'), ('modpicard', 'newton_mixed')],
                              ['(a) ψ-based form', '(b) Mixed form']):
        refline(a, 'polmann')
        for k, dt in enumerate((1, 900, 3000, 5400)):
            r = get('polmann', mp, 2.5, dt)
            x, p = prof('polmann', r)
            a.plot(x, p, color=SHADES[k + 1], lw=1.3, label=f'Picard, Δt = {dt} s')
            rn = get('polmann', mn, 2.5, dt)
            if rn is not None:
                x, p = prof('polmann', rn)
                a.plot(x[::3], p[::3], 'o', mfc='none', color=SHADES[k + 1], ms=4)
        if mp == 'modpicard':
            x, p = prof('polmann', get('polmann', 'lscheme', 2.5, 900))
            a.plot(x[1::3], p[1::3], 'x', color='#d62728', ms=5, label='L-scheme, Δt = 900 s')
        a.plot([], [], 'o', mfc='none', color='grey', label='Newton (same Δt)')
        a.set(xlabel='Depth (cm)', title=t, xlim=(0, 100)); a.legend(loc='lower right')
    ax[0].set_ylabel('Pressure head (cm)')
    fig.tight_layout(); fig.savefig(FIG / 'Fig06_polmann_iterative.png'); plt.close(fig)


def fig7():
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for a, dt, ms in zip(ax, (900, 1), (['linimp', 'picard_psi', 'modpicard', 'lscheme'], ['explicit', 'linimp', 'picard_psi', 'modpicard'])):
        refline(a, 'polmann')
        for m in ms:
            r = get('polmann', m, 2.5, dt)
            if r is None:
                continue
            x, p = prof('polmann', r)
            style = dict(ls='--') if m == 'lscheme' else {}
            a.plot(x, p, color=COL[m], lw=1.3, label=LAB[m], **style)
        a.set(xlabel='Depth (cm)', title=f'Δt = {dt} s', xlim=(0, 100)); a.legend(loc='lower right')
    ax[0].set_ylabel('Pressure head (cm)')
    fig.tight_layout(); fig.savefig(FIG / 'Fig07_polmann_all_solvers.png'); plt.close(fig)


def fig8():
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    dts = [1, 270, 900, 3000, 5400]
    for m in ('linimp', 'picard_psi', 'modpicard'):
        xs, ys = [], []
        for dt in dts:
            r = get('polmann', m, 2.5, dt)
            if r is not None:
                xs.append(dt); ys.append(r['MB'])
        ax.semilogx(xs, ys, 'o-', color=COL[m], label=LAB[m])
    ax.axhline(1, color='k', lw=.7)
    ax.set(xlabel='Time step Δt (s)', ylabel='Mass balance ratio ΔS/Q$_{net}$ (−)', yscale='log')
    ax.legend(title='Newton and L-schemes coincide with\nthe Picard ratio of the same form', title_fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / 'Fig08_polmann_mass_balance.png'); plt.close(fig)


def fig10():
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    specs = [[('linimp', .0125, .001, 'Implicit non-iterative, Δt = 0.001 d'), ('picard_psi', .0125, .005, 'Picard ψ, Δt = 0.005 d'),
              ('picard_psi', .0125, .01, 'Picard ψ, Δt = 0.01 d')],
             [('modpicard', .0125, .001, 'Picard, Δt = 0.001 d'), ('modpicard', .0125, .002, 'Picard, Δt = 0.002 d'),
              ('lnewton', .0125, .005, 'L/Newton, Δt = 0.005 d')]]
    titles = ['(a) ψ-based form (Picard fails for Δt ≤ 0.002 d)', '(b) Mixed form (Picard fails for Δt ≥ 0.005 d)']
    for a, sp, t in zip(ax, specs, titles):
        refline(a, 'miller', depth=False, swap=True)
        lines(a, 'miller', sp, swap=True, depth=False)
        a.set(xlabel='Pressure head (m)', title=t); a.set_xlim(left=-5.5); a.legend(loc='upper left', fontsize=6.5)
    ax[0].set_ylabel('Elevation above the water table (m)')
    fig.tight_layout(); fig.savefig(FIG / 'Fig10_miller_profiles.png'); plt.close(fig)


def fig11():
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    dts = [.001, .002, .005, .01]
    ms = ('linimp', 'picard_psi', 'newton_psi', 'modpicard', 'newton_mixed', 'lscheme', 'lnewton')
    for k, m in enumerate(ms):
        first = True
        for j, dt in enumerate(dts):
            r = load('miller', tag(m, .0125, dt))
            x = j + (k - 3) * .11
            ok = r['status'] == 'completed'
            ax.semilogy(x, r['MB'] if ok else 0.3, 'o' if ok else 'x', color=COL[m], mfc='none' if 'newton' in m else COL[m],
                        label=LAB[m] if first else None)
            first = False
    ax.axhline(1, color='k', lw=.7)
    ax.set_xticks(range(4)); ax.set_xticklabels([f'{d} d' for d in dts])
    ax.set(xlabel='Time step', ylabel='Mass balance ratio (−)', ylim=(.15, 5e5))
    ax.text(3.5, .22, '× : time step failed to converge', fontsize=7, ha='right')
    ax.legend(fontsize=6.5, loc='center left', bbox_to_anchor=(1.01, .5))
    fig.tight_layout(); fig.savefig(FIG / 'Fig11_miller_mass_balance.png'); plt.close(fig)


def lehmann_axes(a, t):
    a.set_xscale('symlog', linthresh=10)
    a.set(xlabel='Pressure head (cm)', title=t, ylim=(180, 0), xlim=(-3e5, 0))
    a.legend(loc='lower left')


def fig12():
    fig, ax = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    refline(ax[0], 'lehmann', swap=True); refline(ax[1], 'lehmann', swap=True)
    lines(ax[0], 'lehmann', [('newton_psi', 2., 1., 'Newton ψ (Picard ψ fails)'), ('linimp', 2., 1., 'Implicit non-iterative')], swap=True)
    lines(ax[1], 'lehmann', [('modpicard', 2., 1., 'Picard'), ('lscheme', 2., 1., 'L-scheme')], swap=True)
    lehmann_axes(ax[0], '(a) ψ-based form, Δz = 2 cm'); lehmann_axes(ax[1], '(b) Mixed form, Δz = 2 cm')
    ax[0].set_ylabel('Depth (cm)')
    fig.tight_layout(); fig.savefig(FIG / 'Fig12_lehmann_dz2.png'); plt.close(fig)


def fig13():
    fig, ax = plt.subplots(figsize=(5.5, 4))
    refline(ax, 'lehmann', swap=True)
    lines(ax, 'lehmann', [('modpicard', dz, 1., f'Δz = {dz:g} cm') for dz in (1., 2.)], swap=True)
    ax.text(-20, 150, 'Δz = 5 and 10 cm: steps failed\nto converge (days 33–34)', fontsize=7, ha='right')
    lehmann_axes(ax, 'Mixed form, Picard, Δt = 1 day')
    ax.set_ylabel('Depth (cm)')
    fig.tight_layout(); fig.savefig(FIG / 'Fig13_lehmann_dz.png'); plt.close(fig)


def fig14():
    ref = load('ireson', 'ref1')
    d0 = date(1999, 10, 1)
    days = np.array([d0 + timedelta(days=int(k)) for k in range(len(ref['daily_S']))])
    hyd = hydrus_storage() * 1000
    fig, ax = plt.subplots(3, 1, figsize=(10, 7.5))
    series = [('modpicard', 'Mixed form (Picard; Newton, L-scheme and L/Newton identical)'), ('picard_psi', 'ψ-based form (Picard)'),
              ('linimp', 'Implicit non-iterative')]
    ax[0].plot(days, ref['daily_S'] * 1000, 'k', lw=1.6, label='Reference')
    ax[0].plot(days[1:3653], hyd, color='#17becf', lw=1, label='HYDRUS-1D')
    for m, lab in series:
        r = get('ireson', m, .05, 1.)
        ax[0].plot(days, r['daily_S'] * 1000, color=COL[m], lw=.9, label=lab)
        ax[1].plot(days, (r['daily_S'] - ref['daily_S']) * 1000, color=COL[m], lw=.9, label=lab)
        sel = np.array([d.year == 2004 for d in days])
        ax[2].plot(days[sel], r['daily_S'][sel] * 1000, color=COL[m], lw=1)
    ax[1].plot(days[1:3653], hyd - ref['daily_S'][1:3653] * 1000, color='#17becf', lw=.9, label='HYDRUS-1D')
    sel = np.array([d.year == 2004 for d in days])
    ax[2].plot(days[sel], ref['daily_S'][sel] * 1000, 'k', lw=1.6)
    ax[2].plot(days[1:3653][sel[1:3653]], hyd[sel[1:3653]], color='#17becf', lw=1)
    ax[0].set(ylabel='Storage (mm)', title='(a) Ten-year record'); ax[0].legend(ncol=2, fontsize=7)
    ax[1].set(ylabel='Difference from\nreference (mm)', title='(b) Storage error'); ax[1].legend(ncol=2, fontsize=7)
    ax[2].set(ylabel='Storage (mm)', title='(c) 2004')
    fig.tight_layout(); fig.savefig(FIG / 'Fig14_ireson_storage.png'); plt.close(fig)


def fig9():
    rows = json.load(open(OUT / 'polmann' / 'summary.json'))
    fig, ax = plt.subplots(figsize=(6, 4))
    for m in ('explicit', 'linimp', 'picard_psi', 'newton_psi', 'modpicard', 'newton_mixed', 'lscheme', 'lnewton'):
        rs = [r for r in rows if r['method'] == m and r['status'] == 'completed' and r['dz'] == 2.5]
        if not rs:
            continue
        mk = 's' if 'newton' in m else ('^' if m == 'lscheme' else 'o')
        ax.loglog([r['runtime'] for r in rs], [r['theta_rmse'] for r in rs], mk, color=COL[m], label=LAB[m],
                  mfc='none' if 'newton' in m else COL[m])
        for r in rs:
            ax.annotate(f"{r['dt']:g}", (r['runtime'], r['theta_rmse']), fontsize=6, xytext=(3, 2), textcoords='offset points')
    rs = [r for r in rows if r['method'] == 'modpicard' and r['dz'] < 2.5]
    ax.loglog([r['runtime'] for r in rs], [r['theta_rmse'] for r in rs], 'D', color='#2ca02c', mfc='white', label='Picard (mixed), Δz = 1.25, 0.625 cm')
    ax.set(xlabel='Run time (s)', ylabel='θ RMSE against reference (−)', title='Polmann benchmark (labels: Δt in s)')
    ax.legend(fontsize=6.5)
    fig.tight_layout(); fig.savefig(FIG / 'Fig09_polmann_error_vs_runtime.png'); plt.close(fig)


def fig15():
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    dts = [1, 900, 3000, 5400]
    for m in ('picard_psi', 'newton_psi', 'modpicard', 'newton_mixed', 'lscheme', 'lnewton'):
        xs, ys = [], []
        for dt in dts:
            r = get('polmann', m, 2.5, dt)
            if r is not None:
                xs.append(dt); ys.append(r['it_mean'])
        ax[0].loglog(xs, ys, ('s--' if 'newton' in m else 'o-'), color=COL[m], label=LAB[m], mfc='none' if 'newton' in m else COL[m])
    ax[0].set(xlabel='Time step Δt (s)', ylabel='Mean iterations per step', title='(a) Polmann')
    ax[0].legend(fontsize=6.5)
    base = [('Warrick', 'warrick', 5., 900), ('Polmann', 'polmann', 2.5, 900), ('Miller', 'miller', .0125, .001),
            ('Lehmann', 'lehmann', 2., 1.), ('Ireson', 'ireson', .05, 1.)]
    ms = ['picard_psi', 'newton_psi', 'modpicard', 'newton_mixed', 'lscheme', 'lnewton']
    w = .13
    for k, m in enumerate(ms):
        for j, (lab, c, dz, dt) in enumerate(base):
            r = load(c, tag(m, dz, dt))
            x = j + (k - 2.5) * w
            if r['status'] == 'completed':
                ax[1].bar(x, r['it_mean'], w, color=COL[m], hatch='//' if 'newton' in m else None,
                          edgecolor='white', label=LAB[m] if j == 1 else None)
            else:
                ax[1].text(x, 1.2, 'F', ha='center', fontsize=7, color=COL[m], fontweight='bold')
    ax[1].set_yscale('log'); ax[1].set_ylim(1, 2e4)
    ax[1].set_xticks(range(5)); ax[1].set_xticklabels([f'{b[0]}\n(Δt = {b[3]:g})' for b in base], fontsize=7.5)
    ax[1].set(ylabel='Mean iterations per step', title='(b) All benchmarks (F = failed)')
    ax[1].legend(fontsize=6, ncol=2)
    fig.tight_layout(); fig.savefig(FIG / 'Fig15_iterations.png'); plt.close(fig)


if __name__ == '__main__':
    import sys
    sel = sys.argv[1:] or ['fig2', 'fig3', 'fig4', 'fig5', 'fig6', 'fig7', 'fig8', 'fig10', 'fig11', 'fig12', 'fig13', 'fig14', 'fig9', 'fig15']
    for f in sel:
        globals()[f](); print('done', f)
    raise SystemExit
    # extra numbers for the text
    c = R.make_case('polmann')
    print('Polmann explicit 50 s:', R.run(c, 'explicit', 50)['status'])
    for case in ('polmann', 'warrick', 'miller'):
        print(case, 'reference front depth:', R.front_depth(R.make_case(case), load(case, 'ref1')['z'], load(case, 'ref1')['theta']))
    for m in ('modpicard', 'picard_psi', 'linimp'):
        r = load('ireson', tag(m, .05, 1.))
        print('Ireson', m, 'Qnet', r['Qnet'], 'dS', r['dS'], 'epsB', r['epsB'])
