"""Run references and all scheme/step combinations for one benchmark.
Usage: python run_all.py <case> refs|runs|summ"""
import json, sys, time
from dataclasses import replace
from pathlib import Path
import numpy as np
import richards_revised as R

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
ITER = ['picard_psi', 'modpicard', 'newton_psi', 'newton_mixed', 'lscheme', 'lnewton']
REF = {  # two refinement levels (dz factor, dt); the finer one is the reference, the other its check
    'warrick': [(16, 10.), (32, 5.)],
    'polmann': [(16, 4.5), (32, 2.25)],
    'miller':  [(8, 1e-4), (16, 5e-5)],
    'lehmann': [(8, 1 / 48), (16, 1 / 96)],
    'ireson':  [(4, 1 / 12), (8, 1 / 24)],
}
RUNS = {
    'warrick': [('explicit', 5., dt) for dt in (1, 60, 300, 900, 1800)] + [('linimp', 5., dt) for dt in (1, 900, 2400)]
               + [(m, 5., dt) for m in ITER for dt in (900, 2400)],
    'polmann': [('explicit', 2.5, dt) for dt in (1, 42, 60, 90, 126)] + [('linimp', 2.5, dt) for dt in (1, 270, 900, 3000, 5400)]
               + [(m, 2.5, dt) for m in ITER[:4] for dt in (1, 900, 3000, 5400)]
               + [(m, 2.5, dt) for m in ITER[4:] for dt in (900, 3000, 5400)]
               + [('modpicard', dz, 900) for dz in (1.25, 0.625)],
    'miller':  [('explicit', .0125, .001)] + [(m, .0125, dt) for m in ['linimp'] + ITER for dt in (.001, .002, .005, .01)],
    'lehmann': [(m, dz, 1.) for m in ('picard_psi', 'modpicard') for dz in (1., 2., 5., 10.)]
               + [(m, 2., 1.) for m in ('linimp', 'newton_psi', 'newton_mixed', 'lscheme', 'lnewton')],
    'ireson':  [(m, .05, 1.) for m in ['linimp'] + ITER],
}


def tag(m, dz, dt):
    return f'{m}_dz{dz:g}_dt{dt:g}'


def save(case, name, r):
    d = OUT / case
    d.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(d / f'{name}.npz', z=r['z'], psi=r['psi'], theta=r['theta'], daily_S=r['daily_S'])
    meta = {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in r.items()
            if k not in ('z', 'psi', 'theta', 'daily_S')}
    (d / f'{name}.json').write_text(json.dumps(meta, indent=1, default=float))


def load(case, name):
    d = OUT / case
    a = dict(np.load(d / f'{name}.npz'))
    a.update(json.loads((d / f'{name}.json').read_text()))
    return a


def tv_excess(case, z, th, ref):
    """Total variation of the profile (with boundary values) minus that of the reference."""
    s = case.soil
    def tv(zz, tt):
        top = [float(s.theta(case.top_head))] if case.top_head is not None else []
        bot = [float(s.theta(case.bottom_head))] if case.bottom_head is not None else []
        prof = np.r_[bot, tt, top]
        return float(np.sum(np.abs(np.diff(prof))))
    return tv(z, th) - tv(z, np.interp(z, ref['z'], ref['theta']))


def refs(name):
    base = R.make_case(name)
    for k, (f, dt) in enumerate(REF[name]):
        if (OUT / name / f'ref{k}.json').exists():
            continue
        c = replace(base, dz=base.dz / f)
        meth = 'newton_mixed' if name == 'ireson' else 'lnewton'
        r = R.run(c, meth, dt, tolF=1e-10, tolH=1e-9, adapt=True, linesearch=True, wall_limit=float('inf'))
        print(f'{name} reference level {k}: dz={c.dz:g} dt={dt:g} method={meth} status={r["status"]} '
              f'it/step={r["it_mean"]:.1f} steps={r["n_steps"]} runtime={r["runtime"]:.0f}s MB={r["MB"]:.10f}', flush=True)
        if r['status'] == 'completed':
            save(name, f'ref{k}', r)


def hydrus_storage():
    rows = []
    for line in open(HERE.parent / 'notebooks' / 'ireson' / 'T_Level.out'):
        p = line.split()
        try:
            rows.append((float(p[0]), float(p[16])))
        except (ValueError, IndexError):
            continue
    t, v = np.array(rows).T
    days = np.arange(1, 3653)
    return np.array([v[np.where(np.isclose(t, d))[0][-1]] if np.any(np.isclose(t, d)) else np.nan for d in days])


def runs(name):
    base = R.make_case(name)
    for m, dz, dt in RUNS[name]:
        if (OUT / name / f'{tag(m, dz, dt)}.json').exists():
            continue
        r = R.run(replace(base, dz=dz), m, dt, wall_limit=float('inf'))
        save(name, tag(m, dz, dt), r)
        print(f"{name:8s} {m:12s} dz={dz:<7g} dt={dt:<7g} {r['status']:9s} it/step={r['it_mean']:8.1f} "
              f"t={r['runtime']:7.2f}s MB={r['MB']:.4f} {r['reason'][:80]}", flush=True)
    print('ALL RUNS DONE')


def summ(name):
    base = R.make_case(name)
    ref, chk = load(name, 'ref1'), load(name, 'ref0')
    rows = []
    unc = R.errors(replace(base, dz=float(chk['dz'])), chk, ref)
    unc.update(case=name, method='reference check', dz=float(chk['dz']), dt=float(chk['dt']), status='completed')
    if base.flux is not None:
        n = min(len(chk['daily_S']), len(ref['daily_S']))
        es = chk['daily_S'][:n] - ref['daily_S'][:n]
        unc.update(S_rmse=float(np.sqrt(np.mean(es ** 2))), S_max=float(np.max(np.abs(es))))
    rows.append(unc)
    hyd = hydrus_storage() if name == 'ireson' else None
    for m, dz, dt in RUNS[name]:
        c = replace(base, dz=dz)
        r = load(name, tag(m, dz, dt))
        row = {k: r[k] for k in ('case', 'method', 'dz', 'dt', 'status', 'reason', 't_end', 'runtime', 'it_total',
                                 'it_mean', 'it_max', 'n_steps', 'MB', 'MB_endstep', 'epsB', 'Qnet', 'dS')}
        if r['status'] == 'completed':
            row.update(R.errors(c, r, ref))
            row['tv_excess'] = tv_excess(c, r['z'], r['theta'], ref)
            if c.flux is not None:
                n = min(len(r['daily_S']), len(ref['daily_S']))
                es = r['daily_S'][:n] - ref['daily_S'][:n]
                row.update(S_rmse=float(np.sqrt(np.mean(es ** 2))), S_bias=float(np.mean(es)), S_max=float(np.max(np.abs(es))))
                if hyd is not None:
                    eh = r['daily_S'][1:3653] - hyd
                    row.update(S_rmse_hydrus=float(np.sqrt(np.nanmean(eh ** 2))), S_bias_hydrus=float(np.nanmean(eh)))
        rows.append(row)
    if hyd is not None:
        eh = ref['daily_S'][1:3653] - hyd
        rows.append(dict(case=name, method='reference vs HYDRUS-1D', S_rmse_hydrus=float(np.sqrt(np.nanmean(eh ** 2))),
                         S_bias_hydrus=float(np.nanmean(eh))))
    (OUT / name / 'summary.json').write_text(json.dumps(rows, indent=1, default=float))
    print(f'{name}: summary of {len(rows)} rows written')


if __name__ == '__main__':
    {'refs': refs, 'runs': runs, 'summ': summ}[sys.argv[2]](sys.argv[1])
