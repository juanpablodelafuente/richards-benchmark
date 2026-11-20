import ast, numpy as np, time, sys
from dataclasses import replace
import json
from pathlib import Path
import richards_revised as R
NB = Path(__file__).resolve().parent.parent / 'notebooks'
def nb_source(path):
    """Python code of a Jupyter notebook (code cells only, IPython magics removed)."""
    cells = json.loads(Path(path).read_text(encoding='utf8'))['cells']
    lines = [l for c in cells if c['cell_type'] == 'code' for l in ''.join(c['source']).splitlines() if not l.lstrip().startswith(('%', '!'))]
    return '\n'.join(lines) + '\n'
def defs(path):
    src = nb_source(path); t = ast.parse(src)
    g = {}; exec(ast.unparse(ast.Module(body=[n for n in t.body if isinstance(n, (ast.FunctionDef, ast.Import, ast.ImportFrom))], type_ignores=[])), g); return g
# --- Polmann: notebook vs revised framework (same algorithms where the notebook was correct)
g = defs(NB / 'polmann' / 'Polmann_benchmark.ipynb'); g['pars'] = g['setpars']()
c = R.make_case('polmann')
for nbm, rm, dt in [('modpicard', 'modpicard', 900), ('picard', 'picard_psi', 900), ('implicit', 'linimp', 270), ('implicit', 'linimp', 900)]:
    z, t, dz, n, nt, zN, psi, psiB, psiT, pars = g['setup'](dt)
    nb = g['ModelRun_' + nbm](dt, dz, n, nt, psi, psiB, psiT, pars)
    r = R.run(c, rm, dt)
    print(f"Polmann {rm:10s} dt={dt:5d}: max|Δψ| notebook vs revised = {np.max(np.abs(nb[0][-1] - r['psi'])):.2e} cm; "
          f"MB notebook {nb[-1]:.4f} | revised end-step {r['MB_endstep']:.4f} | revised consistent {r['MB']:.4f}; status {r['status']}, it_mean {r['it_mean']:.1f}")
# Newton (complete Jacobian) must converge to the same discrete solution as Picard, quadratically
for m in ['newton_psi', 'newton_mixed', 'lscheme', 'lnewton']:
    r = R.run(c, m, 900); rp = R.run(c, 'picard_psi' if m == 'newton_psi' else 'modpicard', 900)
    print(f"Polmann {m:12s} dt=900: status {r['status']}, it/step {r['it_mean']:.1f} (max {r['it_max']}), max|Δψ| vs Picard {np.max(np.abs(r['psi'] - rp['psi'])):.1e}, {r['runtime']:.2f} s")
# --- Lehmann modified Picard, dz = 2 cm
src = nb_source(NB / 'lehmann' / 'Lehmann_Picard_mixed_form_RE.ipynb').replace('np.linalg.solve(A, R)', '__import__("numpy").linalg.solve(A, R)')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; plt.show = lambda *a, **k: None
gl = {'__name__': 'nb'}; exec(src, gl)
r = R.run(R.make_case('lehmann'), 'modpicard', 1.0)
print(f"Lehmann modpicard dz=2: max|Δψ| notebook vs revised = {np.max(np.abs(gl['psi'][-1] - r['psi'])):.2e} cm; MB {r['MB']:.6f}; it_mean {r['it_mean']:.1f}")
# --- Warrick explicit, dt = 900 s: notebook update loop vs revised (same grid and bottom treatment)
gw = defs(NB / 'warrick' / 'Warrick__explicit.ipynb')
for k in ['nz', 'dz', 'wet', 'dry', 'thr', 'ths', 'alpha', 'rksat', 'avg', 'rm', 'rn']:
    pass
exec("nz=25\ndz=5\nwet=0.495\ndry=0.24\nthr=0.124\nths=0.495\nalpha=0.015\nrksat=1.23e-5\navg=0\nrm=0.5\nrn=1/(1-rm)", gw)
water = np.full(25, 0.24); t = 0
while t < 360000:
    t += 900; water = gw['update'](0.24, 900, 900 / 5, 5, 25, 0.495, water)
r = R.run(R.make_case('warrick'), 'explicit', 900)
# notebook nodes: depths 5..125 (node 25 copies node 24); revised unknowns: depths 120..5
print(f"Warrick explicit dt=900: max|Δθ| notebook vs revised = {np.max(np.abs(water[:24] - r['theta'][::-1])):.2e}; status {r['status']}")
