"""Reproduce the archived benchmark results without replacing them.

Examples (from revised_solver):
    python reproduce.py --output reproductions/laptop
    python reproduce.py --output reproductions/check --cases polmann --no-figures
    python reproduce.py --output reproductions/full --recompute-references

References are copied from the archive unless --recompute-references is supplied.
The numerical implementation and tolerances are those of the supplied package.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
import numpy as np
import scipy
import run_all as A

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / "results"
CASES = list(A.RUNS)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def environment():
    config = io.StringIO()
    with contextlib.redirect_stdout(config):
        np.show_config()
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=HERE, text=True,
            stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=HERE, text=True))
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    processor = platform.processor()
    if not processor and Path("/proc/cpuinfo").exists():
        processor = next((s.split(":", 1)[1].strip() for s in
                          Path("/proc/cpuinfo").read_text().splitlines()
                          if s.startswith("model name")), "unknown")
    files = [HERE / n for n in ("richards_revised.py", "run_all.py", "make_figures.py", "reproduce.py")]
    files += [HERE.parent / "notebooks" / "ireson" / n for n in ("infiltration.dat", "T_Level.out")]
    return dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
                python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                matplotlib=matplotlib.__version__, operating_system=platform.platform(),
                processor=processor or "unknown", logical_cpus=os.cpu_count(),
                numpy_build=config.getvalue(), git_commit=commit, working_tree_modified=dirty,
                thread_environment={k: os.environ.get(k) for k in
                                    ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
                file_sha256={str(p.relative_to(HERE.parent)): digest(p) for p in files if p.exists()})


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=True) + "\n", encoding="utf-8")


def export_csv(results, destination, cases):
    rows = []
    for case in cases:
        rows.extend(json.loads((results / case / "summary.json").read_text()))
    preferred = ["case", "method", "dz", "dt", "status", "reason", "theta_rmse", "theta_max",
                 "psi_rmse", "psi_max", "front_err", "S_rmse", "MB", "epsB", "Qnet", "dS",
                 "it_mean", "it_max", "it_total", "n_steps", "runtime"]
    keys = sorted(set().union(*(r.keys() for r in rows)) - set(preferred))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=preferred + keys)
        w.writeheader()
        w.writerows(rows)


def compare(results, cases):
    """Flag differences for inspection; tolerances here are regression checks, not error estimates."""
    rows = []
    for case in cases:
        for method, dz, dt in A.RUNS[case]:
            stem = A.tag(method, dz, dt)
            old = json.loads((ARCHIVE / case / (stem + ".json")).read_text())
            new = json.loads((results / case / (stem + ".json")).read_text())
            row = dict(case=case, run=stem, status_matches=new["status"] == old["status"],
                       end_time_matches=bool(np.isclose(new["t_end"], old["t_end"], rtol=1e-12, atol=1e-12)),
                       counts_match=all(new[k] == old[k] for k in ("n_steps", "it_total", "it_max")),
                       archived_runtime=old["runtime"], rerun_runtime=new["runtime"])
            # A failed run is compared at the same accepted time only; it is not a final solution.
            if row["end_time_matches"]:
                with np.load(ARCHIVE / case / (stem + ".npz")) as a, np.load(results / case / (stem + ".npz")) as b:
                    for key in ("psi", "theta", "daily_S"):
                        row[key + "_close"] = bool(np.allclose(a[key], b[key], rtol=1e-6, atol=1e-8, equal_nan=True))
                        row[key + "_max_difference"] = float(np.nanmax(np.abs(a[key] - b[key])))
                row["mass_balance_close"] = all(bool(np.isclose(old[k], new[k], rtol=1e-6, atol=1e-8, equal_nan=True))
                                                for k in ("dS", "Qnet", "epsB"))
            row["review_required"] = not all(v for k, v in row.items() if k.endswith(("_matches", "_match", "_close")))
            rows.append(row)
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--output", type=Path, required=True, help="New directory. An existing directory is never overwritten.")
    p.add_argument("--cases", nargs="+", choices=CASES, default=CASES)
    p.add_argument("--recompute-references", action="store_true")
    p.add_argument("--no-figures", action="store_true")
    args = p.parse_args()
    dest = args.output.resolve()
    if dest == HERE or dest == ARCHIVE or ARCHIVE in dest.parents:
        p.error("Choose a separate reproduction directory outside the archived results.")
    if dest.exists():
        p.error("Output already exists. Choose a new name to preserve previous measurements.")
    for name in ("infiltration.dat", "T_Level.out"):
        if "ireson" in args.cases and not (HERE.parent / "notebooks" / "ireson" / name).is_file():
            p.error("Missing Ireson inputs. Run from a complete checkout of richards-benchmark.")
    dest.mkdir(parents=True)
    A.OUT = dest / "results"
    info = environment()
    info.update(cases=args.cases, reference_policy="recomputed" if args.recompute_references else "copied from archived results",
                timings="One serial measurement per configuration; not repeated timing statistics.", state="running")
    info["reference_sha256"] = {}
    write_json(dest / "environment.json", info)
    (dest / "requirements-measured.txt").write_text(
        f"numpy=={np.__version__}\nscipy=={scipy.__version__}\nmatplotlib=={matplotlib.__version__}\n", encoding="utf-8")
    for case in args.cases:
        if args.recompute_references:
            A.refs(case)
        else:
            (A.OUT / case).mkdir(parents=True, exist_ok=True)
            for name in ("ref0.json", "ref0.npz", "ref1.json", "ref1.npz"):
                source = ARCHIVE / case / name
                shutil.copy2(source, A.OUT / case / name)
                info["reference_sha256"][f"{case}/{name}"] = digest(source)
        A.runs(case)
        A.summ(case)
        write_json(dest / "environment.json", info)
    export_csv(A.OUT, dest / "tables" / "all_results.csv", args.cases)
    differences = compare(A.OUT, args.cases)
    write_json(dest / "comparison.json", differences)
    if not args.no_figures:
        if set(args.cases) == set(CASES):
            import make_figures as F
            F.FIG = dest / "figures"
            F.FIG.mkdir()
            for n in range(2, 16):
                getattr(F, f"fig{n}")()
                print(f"Figure {n} written", flush=True)
        else:
            print("Full figure set skipped for a subset of cases.", flush=True)
    info["state"] = "completed"
    info["completed_utc"] = datetime.now(timezone.utc).isoformat()
    info["runs_requiring_review"] = sum(r["review_required"] for r in differences)
    write_json(dest / "environment.json", info)
    print(f"Saved to {dest}. Runs requiring review: {info['runs_requiring_review']}", flush=True)
    print("Inspect comparison.json before transferring any numbers to the manuscript.", flush=True)


if __name__ == "__main__":
    main()
