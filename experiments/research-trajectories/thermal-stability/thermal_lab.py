#!/usr/bin/env python3
"""Standard-library scratch investigation; synthetic outputs, not thermal data.

Run: python3 thermal_lab.py
Writes results.json and traces.csv next to this file. See predictions.json for
predictions frozen before the first run, and trajectories.md for dependencies.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import random
import time

HERE = Path(__file__).resolve().parent
ALPHA = 0.01
VERSION = "thermal-lab-v1"
COUNTS = {"euler_cell_updates": 0, "filter_cell_updates": 0}


def euler(values, r):
    """One simultaneous periodic stencil update; never update in place."""
    n = len(values)
    COUNTS["euler_cell_updates"] += n
    return [values[j] + r * (values[(j-1) % n] - 2*values[j]
                             + values[(j+1) % n]) for j in range(n)]


def average(values):
    n = len(values)
    COUNTS["filter_cell_updates"] += n
    return [(values[(j-1) % n] + 2*values[j] + values[(j+1) % n])/4
            for j in range(n)]


def advance_output(values, output_dt, alpha=ALPHA, length=1.0, max_r=0.4):
    """Split an output interval while retaining the original PDE/stencil.

    Stability margin alone supplies no requested physical-accuracy tolerance.
    For these periodic even grids max_r<=0.5 is the sharp all-mode bound.
    """
    if output_dt <= 0 or length <= 0 or alpha < 0 or not 0 < max_r <= 0.5:
        raise ValueError("Require positive dt/length, alpha>=0 and 0<max_r<=0.5")
    count = max(1, math.ceil(alpha*output_dt*len(values)**2/(max_r*length**2)))
    internal_dt = output_dt/count
    r = alpha*internal_dt/(length/len(values))**2
    for _ in range(count):
        values = euler(values, r)
    return values, {"substeps": count, "internal_dt": internal_dt, "r": r}


def sine(n, k=1):
    return [math.sin(2*math.pi*k*j/n) for j in range(n)]


def amplitude(values, k):
    n = len(values)
    if n % 2 == 0 and k == n//2:
        return math.fsum((-1)**j * value for j, value in enumerate(values))/n
    return 2*math.fsum(value*math.sin(2*math.pi*k*j/n)
                      for j, value in enumerate(values))/n


def gain(n, k, r):
    return 1-4*r*math.sin(math.pi*k/n)**2


def snapshot(name, values, t, k):
    n = len(values)
    return {"case": name, "time": t, "N": n, "observed_mode": k,
            "mode_amplitude": amplitude(values, k),
            "smooth_amplitude": amplitude(values, 1),
            "mean": math.fsum(values)/n,
            "mean_square": math.fsum(value*value for value in values)/n,
            "max_abs": max(map(abs, values))}


def evolve(name, n, method="original", k=None, steps=10):
    k = n//2 if k is None else k
    perturbation = [(-1)**j for j in range(n)] if k == n//2 else sine(n, k)
    values = [a+0.001*b for a, b in zip(sine(n), perturbation)]
    rows = [snapshot(name, values, 0.0, k)]
    settings = {"N": n, "dx": 1/n, "alpha": ALPHA,
                "output_dt": 0.1, "steps": steps, "perturbation_mode": k,
                "perturbation_amplitude": 0.001, "method": method}
    for step in range(1, steps+1):
        if method == "substepped":
            values, split = advance_output(values, 0.1)
            settings.update(split)
        else:
            r = ALPHA*0.1*n*n
            values = euler(values, r)
            if method == "filtered":
                values = average(values)
            settings.update({"r": r, "internal_dt": 0.1, "substeps": 1})
        rows.append(snapshot(name, values, step*0.1, k))
    return {"settings": settings, "initial": rows[0], "final": rows[-1]}, rows


def main():
    started = time.perf_counter()
    checks, experiments, traces = [], [], []

    def check(name, inputs, source, expected, observed, passed):
        checks.append({"id": name, "artifact_version": VERSION,
                       "inputs": inputs, "expectation_source": source,
                       "expected": expected, "observed": observed,
                       "pass": bool(passed)})

    definitions = [("coarse-contaminated",20,"original",10),
                   ("fine-contaminated",80,"original",40),
                   ("fine-substepped",80,"substepped",40),
                   ("filter-original",80,"filtered",40),
                   ("filter-transfer-witness",80,"filtered",20)]
    by_name = {}
    for name, n, method, k in definitions:
        summary, rows = evolve(name,n,method,k)
        experiments.append(summary)
        traces.extend(rows)
        by_name[name] = rows

    for name, n in [("coarse-contaminated",20),("fine-contaminated",80)]:
        rows = by_name[name]
        observed = rows[1]["mode_amplitude"]/rows[0]["mode_amplitude"]
        expected = gain(n,n//2,ALPHA*0.1*n*n)
        check(name+"-gain",{"N":n,"dt":0.1},"exact Fourier eigenvalue",
              expected,observed,abs(observed-expected)<1e-10)
    fine3 = by_name["fine-contaminated"][3]["mode_amplitude"]
    expected3 = 0.001*(-24.6)**3
    check("three-step-growth",{"N":80,"time":0.3},"frozen modal recurrence",
          expected3,fine3,abs(fine3-expected3)<1e-9)
    for name in ["coarse-contaminated","fine-substepped"]:
        energy = [row["mean_square"] for row in by_name[name]]
        check(name+"-energy",{"case":name},"all Fourier gains |g|<=1 and Parseval",
              "mean-square nonincreasing",energy,
              all(b <= a+1e-14 for a,b in zip(energy,energy[1:])))
    removed = by_name["filter-original"][1]["mode_amplitude"]
    check("filter-removes-visible-mode",{"N":80,"k":40},"filter multiplier at q=1 is zero",
          0.0,removed,abs(removed)<1e-14)
    rows = by_name["filter-transfer-witness"]
    observed = rows[1]["mode_amplitude"]/rows[0]["mode_amplitude"]
    check("filter-counterexample",{"N":80,"k":20,"dt":0.1},
          "composed multiplier (1-4*r*q)*(1-q), q=1/2",
          -5.9,observed,abs(observed+5.9)<1e-10)
    for r in [0.499,0.5,0.501]:
        initial = [(-1)**j for j in range(20)]
        observed = amplitude(euler(initial,r),10)
        check("threshold-"+str(r),{"N":20,"r":r},"even-grid checkerboard eigenvalue",
              1-4*r,observed,abs(observed-(1-4*r))<1e-14)
    constant = [0.731]*31
    evolved, split = advance_output(constant,0.1)
    check("constant-odd-grid",{"N":31,"dt":0.1},"Laplacian annihilates constants",
          "maximum absolute deviation is zero (tolerance 1e-14)",max(abs(x-constant[0]) for x in evolved),
          max(abs(x-constant[0]) for x in evolved)<1e-14)
    rng = random.Random(42)
    values = [rng.random() for _ in range(31)]
    evolved, split = advance_output(values,0.1)
    residual = (math.fsum(evolved)-math.fsum(values))/len(values)
    check("mean-positive-odd-grid",{"N":31,"dt":0.1,"seed":42,"split":split},
          "periodic stencil sum is zero; convex transfer at 0<=r<=0.5",
          "mean residual <1e-14 and output stays in input range",
          {"mean_residual":residual,"input_range":[min(values),max(values)],
           "output_range":[min(evolved),max(evolved)]},
          abs(residual)<1e-14 and min(evolved)>=min(values) and max(evolved)<=max(values))
    for r in [0.4,0.6]:
        impulse = [1.0]+[0.0]*19
        evolved = euler(impulse,r)
        check("impulse-"+str(r),{"N":20,"r":r},"local transfer weights",
              {"center":1-2*r,"minimum":min(0,1-2*r)},
              {"center":evolved[0],"minimum":min(evolved)},
              abs(evolved[0]-(1-2*r))<1e-14 and abs(min(evolved)-min(0,1-2*r))<1e-14)
    convergence = []
    for n in [20,40,80,160]:
        dt = 0.4/(ALPHA*n*n)
        count = round(1/dt)
        values = sine(n)
        for _ in range(count):
            values = euler(values,ALPHA*dt*n*n)
        reference = [math.exp(-4*math.pi**2*ALPHA)*x for x in sine(n)]
        error = math.sqrt(math.fsum((x-y)**2 for x,y in zip(values,reference))/n)
        convergence.append({"N":n,"dt":dt,"r":0.4,"steps":count,
                            "time":count*dt,"rms_error":error,"cell_updates":n*count})
    ratios = [a["rms_error"]/b["rms_error"] for a,b in zip(convergence,convergence[1:])]
    check("smooth-continuum-refinement",{"N":[20,40,80,160],"r":0.4,"time":1.0},
          "analytic heat sine solution; O(dx^2)+O(dt) with dt proportional to dx^2",
          "successive error ratios near 4 (development interval 3.8..4.2)",
          {"rows":convergence,"ratios":ratios},all(3.8<x<4.2 for x in ratios))

    result = {"artifact_version":VERSION,"evidence":"Synthetic numerical development checks only",
              "equation":"u_t=0.01*u_xx; periodic length 1; x_j=j/N",
              "predictions_sha256":hashlib.sha256((HERE/"predictions.json").read_bytes()).hexdigest(),
              "experiments":experiments,"checks":checks,"convergence":convergence,
              "passed":sum(test["pass"] for test in checks),"total":len(checks),
              "resource_use":{**COUNTS,"wall_seconds":time.perf_counter()-started},
              "limits":["No material measurements or original team solver inspected.",
                        "No resonance mechanism is proved absent from real material.",
                        "Substep stability does not certify the application's accuracy tolerance.",
                        "Cases are development data, not skill-effectiveness evidence.",
                        "Small coefficients can lose relative accuracy once an unstable mode dominates."]}
    (HERE/"results.json").write_text(json.dumps(result,indent=2)+"\n")
    with (HERE/"traces.csv").open("w",newline="") as stream:
        writer = csv.DictWriter(stream,fieldnames=list(traces[0]))
        writer.writeheader()
        writer.writerows(traces)
    print(json.dumps({"checks":f"{result['passed']}/{result['total']}",
                      "experiments":experiments,"convergence":convergence,
                      "resources":result["resource_use"]},indent=2))
    return 0 if result["passed"]==result["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
