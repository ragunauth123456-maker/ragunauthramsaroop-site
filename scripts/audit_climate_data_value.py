#!/usr/bin/env python3
"""Offline editorial and arithmetic tests. Not external assurance."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "research-manuscripts" / "climate-data-value-2026"
main = (DIR / "white-paper.md").read_text(encoding="utf-8")
appendix = (DIR / "technical-appendices.md").read_text(encoding="utf-8")
refs = {int(n) for n in re.findall(r"(?m)^\[(\d+)\]\s", main)}
used = {int(n) for n in re.findall(r"\[(\d+)\]", main + appendix)}
assert refs == set(range(1, 13)), f"Unexpected source register: {refs}"
assert not (used - refs), f"Unlisted references: {used - refs}"
assert len(re.findall(r"https://", main)) >= 12
assert all(w in main.lower() for w in ("counterfactual", "financed emissions", "four-ledger", "hypothetical", "2027", "external peer review"))
assert len(main.split()) > 4_000 and len(appendix.split()) > 2_000
def cashflows(capital, first_benefit, degradation, replacement, residual):
    flows = [-capital]
    for year in range(1, 13):
        value = first_benefit * (1.0-degradation)**(year-1)
        flows.append(value - (replacement if year == 8 else 0) + (residual if year == 12 else 0))
    return flows
def npv(rate, flows):
    return sum(cf/(1+rate)**i for i, cf in enumerate(flows))
def irr(flows):
    low, high = -0.5, 1.5
    for _ in range(110):
        mid = (low+high)/2
        if npv(mid, flows)>0: low=mid
        else: high=mid
    return (low+high)/2
cases = (
    ("downside", 12, 1.6, 0.01, 0.12, 3.2, 0.5, -3.657, 4.39),
    ("base", 12, 2.2, 0.005, 0.10, 2.5, 1.0, 1.818, 13.09),
    ("upside", 12, 2.8, 0.0025, 0.08, 2.0, 1.5, 8.376, 20.06),
)
for name, cap, benefit, degrade, rate, repl, residual, expected_npv, expected_irr in cases:
    flows = cashflows(cap, benefit, degrade, repl, residual)
    value, yield_pct = npv(rate, flows), 100*irr(flows)
    assert abs(value-expected_npv)<0.001, (name,value)
    assert abs(yield_pct-expected_irr)<0.015, (name,yield_pct)
    print(f"PASS {name}: NPV USD {value:+.3f}m, IRR {yield_pct:.2f}%")
assert 40/200*150_000 + 25/100*40_000 == 40_000
assert sum((-5_000,-10_000,7_000,1_000,3_000)) == -4_000
print(f"PASS source register: {len(refs)} sources, {len(used)} referenced entries")
print(f"PASS manuscripts: {len(main.split())} core and {len(appendix.split())} appendix words")
print("PASS numerical and reference checks. External assurance: NOT PERFORMED.")
