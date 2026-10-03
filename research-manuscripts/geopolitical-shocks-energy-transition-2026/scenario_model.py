"""Reproducible fictional microgrid stress test. No facility-specific data.
Cash flows: USD million, 20 annual periods, end-of-year, zero inflation.
"""
import csv
import json
from math import isclose
from pathlib import Path

OUT = Path(__file__).resolve().parent
LITRES = 18_000_000
OPEX_M = 1.8
REPLACEMENT_M = 10.0
REPLACEMENT_YEAR = 10
PERIODS = 20

def npv_cashflow(price_usd_litre, rate, capex_m):
    yearly_m = LITRES * price_usd_litre / 1_000_000 - OPEX_M
    cashflows = [-capex_m]
    for year in range(1, PERIODS + 1):
        cf = yearly_m - (REPLACEMENT_M if year == REPLACEMENT_YEAR else 0)
        cashflows.append(cf)
    return sum(cf / (1 + rate) ** year for year, cf in enumerate(cashflows))

def npv_annuity(price_usd_litre, rate, capex_m):
    yearly_m = LITRES * price_usd_litre / 1_000_000 - OPEX_M
    af = (1 - (1 + rate) ** (-PERIODS)) / rate
    return -capex_m + yearly_m * af - REPLACEMENT_M / (1 + rate) ** REPLACEMENT_YEAR

def breakeven_price(rate, capex_m):
    af = (1 - (1 + rate) ** (-PERIODS)) / rate
    target_net_m = (capex_m + REPLACEMENT_M / (1 + rate) ** REPLACEMENT_YEAR) / af
    return (target_net_m + OPEX_M) * 1_000_000 / LITRES

CASES = [
    ("Lower delivered diesel price", 0.85, 0.08, 145),
    ("Central delivered diesel price", 1.10, 0.08, 145),
    ("Elevated fuel, normal finance", 1.45, 0.08, 145),
    ("Elevated fuel, capex and finance shock", 1.45, 0.14, 174),
]

rows = []
for name, price, rate, capex in CASES:
    value = npv_cashflow(price, rate, capex)
    closed = npv_annuity(price, rate, capex)
    assert isclose(value, closed, abs_tol=1e-8), (name, value, closed)
    rows.append({
        "scenario": name,
        "price_usd_per_litre": price,
        "discount_rate_pct": rate * 100,
        "initial_capex_usd_m": capex,
        "annual_gross_fuel_saving_usd_m": LITRES * price / 1_000_000,
        "annual_net_operating_saving_usd_m": LITRES * price / 1_000_000 - OPEX_M,
        "npv_usd_m": round(value, 3),
        "break_even_fuel_price_usd_per_litre": round(breakeven_price(rate, capex), 4),
    })

annual_pv_gwh = 50 * 8760 * .18 / 1000
assert isclose(annual_pv_gwh, 78.84)
assert isclose(18_000_000 / 75_000_000, .24)

with open(OUT / "scenario_results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
with open(OUT / "scenario_results.json", "w", encoding="utf-8") as f:
    json.dump({
        "model_type": "fictional nominal zero-inflation illustration",
        "as_of": "2026-09-27",
        "independent_verification": "cash-flow NPV agrees with annuity NPV in all cases",
        "pv_scale_check_gwh": annual_pv_gwh,
        "rows": rows,
    }, f, indent=2)

if __name__ == "__main__":
    for row in rows:
        print(f"{row['scenario']}: NPV USD {row['npv_usd_m']:+.3f}m; break-even diesel ${row['break_even_fuel_price_usd_per_litre']:.4f}/L")
    print(f"VERIFIED: {len(rows)} NPV scenarios independently match closed-form annuity calculation")
