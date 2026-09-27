#!/usr/bin/env python3
"""Illustrative petroleum revenue arithmetic. Not a Guyana revenue forecast.

Uses simplified gross-revenue accounting as described in Guyana Revenue Authority's
2026 public explanation of Stabroek: https://gra.gov.gy/royalty-payments-to-guyana-government/

Royalty is paid by the contractor group out of its share. This is a teaching
model, not a substitute for executed PSA accounting, cost audit, individual
project economics, income-tax or regulatory interpretation.
"""
from __future__ import annotations
import csv
from pathlib import Path

def waterfall(barrels: int, price_usd: float, royalty: float,
              recovery_cap: float, requested_cost_fraction: float,
              government_profit_share: float = 0.5) -> dict:
    assert barrels >= 0 and price_usd >= 0
    assert all(0 <= x <= 1 for x in
               (royalty, recovery_cap, requested_cost_fraction, government_profit_share))
    gross = barrels * price_usd
    recovered = gross * min(requested_cost_fraction, recovery_cap)
    profit_pool = gross - recovered
    government_profit = profit_pool * government_profit_share
    royalty_cash = gross * royalty
    contractor_profit_net_of_royalty = profit_pool * (1-government_profit_share) - royalty_cash
    assert abs(recovered + government_profit + royalty_cash
               + contractor_profit_net_of_royalty - gross) <= 1e-6 * max(1, gross)
    return {
        "barrels_illustrative": barrels,
        "price_usd_per_barrel": price_usd,
        "gross_sales_usd": gross,
        "royalty_fraction": royalty,
        "recovery_cap_fraction": recovery_cap,
        "requested_cost_fraction": requested_cost_fraction,
        "actual_cost_recovered_usd": recovered,
        "government_profit_oil_usd": government_profit,
        "government_royalty_usd": royalty_cash,
        "government_total_usd": government_profit + royalty_cash,
        "contractor_cost_recovered_usd": recovered,
        "contractor_profit_after_royalty_usd": contractor_profit_net_of_royalty,
    }

def scenarios() -> list[dict]:
    records = []
    for price in (40, 60, 80):
        for actual_cost in (0.20, 0.50, 0.75):
            r = waterfall(
                barrels=10_000_000, price_usd=float(price),
                royalty=0.02, recovery_cap=0.75,
                requested_cost_fraction=actual_cost,
            )
            r["scenario"] = f"illustrative_stabroek_price_{price}_cost_{int(actual_cost*100)}"
            records.append(r)
    return records

def test_reconciliation() -> None:
    first = waterfall(100, 1, 0.02, 0.75, 0.75)
    assert round(first["government_total_usd"], 4) == 14.5
    assert round(first["contractor_profit_after_royalty_usd"], 4) == 10.5
    lower_cost = waterfall(100, 1, 0.02, 0.75, 0.20)
    assert round(lower_cost["government_total_usd"], 4) == 42.0
    assert lower_cost["government_total_usd"] > first["government_total_usd"]
    assert waterfall(0, 0, .02, .75, .75)["government_total_usd"] == 0

if __name__ == "__main__":
    test_reconciliation()
    rows = scenarios()
    target = Path(__file__).with_name("ILLUSTRATIVE_SCENARIOS.csv")
    with target.open("w", newline="", encoding="utf-8") as handle:
        out = csv.DictWriter(handle, fieldnames=list(rows[0]))
        out.writeheader()
        out.writerows(rows)
    print(f"Wrote {len(rows)} illustrative rows to {target.name}. Tests passed.")
