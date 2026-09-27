#!/usr/bin/env python3
"""Reproducible illustrative models for the Guyana petroleum case study.

These are teaching and stress-test models, not forecasts of Guyana revenue,
operator economics, legal entitlements or future Natural Resource Fund values.

The simplified Stabroek waterfall follows the public explanation of royalty,
cost-recovery ceiling and residual profit-oil sharing described by the Guyana
Revenue Authority. Full publication use remains subject to clause-level review
of the executed PSA, cost-accounting rules and independent petroleum-fiscal
review.

Source register: SOURCE_REGISTER.md, especially S02, S07, S15, S41-S47.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class FundYear:
    year: int
    opening_usd: float
    deposits_usd: float
    return_rate: float
    withdrawals_usd: float

    @property
    def investment_return_usd(self) -> float:
        # Illustrative convention: return applied to opening balance only.
        # Final flagship scenarios should use monthly cash timing.
        return self.opening_usd * self.return_rate

    @property
    def closing_usd(self) -> float:
        return (
            self.opening_usd
            + self.deposits_usd
            + self.investment_return_usd
            - self.withdrawals_usd
        )


def waterfall(
    barrels: int,
    price_usd: float,
    royalty: float,
    recovery_cap: float,
    requested_cost_fraction: float,
    government_profit_share: float = 0.5,
) -> dict:
    """Simplified gross-sales allocation for sensitivity analysis."""
    assert barrels >= 0 and price_usd >= 0
    assert all(
        0 <= x <= 1
        for x in (
            royalty,
            recovery_cap,
            requested_cost_fraction,
            government_profit_share,
        )
    )
    gross = barrels * price_usd
    recovered = gross * min(requested_cost_fraction, recovery_cap)
    profit_pool = gross - recovered
    government_profit = profit_pool * government_profit_share
    royalty_cash = gross * royalty
    contractor_profit_net_of_royalty = (
        profit_pool * (1 - government_profit_share) - royalty_cash
    )
    government_total = government_profit + royalty_cash

    assert abs(
        recovered
        + government_profit
        + royalty_cash
        + contractor_profit_net_of_royalty
        - gross
    ) <= 1e-6 * max(1, gross)

    return {
        "barrels_illustrative": barrels,
        "price_usd_per_barrel": price_usd,
        "gross_sales_usd": gross,
        "royalty_fraction": royalty,
        "recovery_cap_fraction": recovery_cap,
        "requested_cost_fraction": requested_cost_fraction,
        "actual_cost_recovered_usd": recovered,
        "profit_pool_usd": profit_pool,
        "government_profit_oil_usd": government_profit,
        "government_royalty_usd": royalty_cash,
        "government_total_usd": government_total,
        "government_share_of_gross": 0 if gross == 0 else government_total / gross,
        "contractor_cost_recovered_usd": recovered,
        "contractor_profit_after_royalty_usd": contractor_profit_net_of_royalty,
    }


def contract_scenarios() -> list[dict]:
    rows: list[dict] = []
    for price in (40, 60, 80, 100):
        for actual_cost in (0.20, 0.50, 0.65, 0.75):
            r = waterfall(
                barrels=10_000_000,
                price_usd=float(price),
                royalty=0.02,
                recovery_cap=0.75,
                requested_cost_fraction=actual_cost,
            )
            r["scenario"] = (
                f"illustrative_stabroek_price_{price}_cost_{int(actual_cost * 100)}"
            )
            rows.append(r)
    return rows


def production_shock_scenarios() -> list[dict]:
    """Illustrate combined price, volume and cost-recovery sensitivity."""
    rows: list[dict] = []
    base_barrels = 10_000_000
    for volume_factor in (0.70, 0.85, 1.00):
        for price in (40, 60, 80):
            for actual_cost in (0.50, 0.75):
                barrels = int(base_barrels * volume_factor)
                r = waterfall(
                    barrels=barrels,
                    price_usd=float(price),
                    royalty=0.02,
                    recovery_cap=0.75,
                    requested_cost_fraction=actual_cost,
                )
                r["volume_factor"] = volume_factor
                r["scenario"] = (
                    f"combined_volume_{int(volume_factor*100)}"
                    f"_price_{price}_cost_{int(actual_cost*100)}"
                )
                rows.append(r)
    return rows


def fund_path(
    opening_usd: float,
    annual_deposits: Iterable[float],
    annual_withdrawals: Iterable[float],
    annual_returns: Iterable[float],
    start_year: int = 1,
) -> list[dict]:
    deposits = list(annual_deposits)
    withdrawals = list(annual_withdrawals)
    returns = list(annual_returns)
    assert len(deposits) == len(withdrawals) == len(returns)
    assert opening_usd >= 0
    assert all(x >= 0 for x in deposits)
    assert all(x >= 0 for x in withdrawals)
    assert all(-1 < x < 1 for x in returns)

    rows: list[dict] = []
    opening = opening_usd
    for i, (deposit, withdrawal, rate) in enumerate(
        zip(deposits, withdrawals, returns), start=start_year
    ):
        y = FundYear(
            year=i,
            opening_usd=opening,
            deposits_usd=deposit,
            return_rate=rate,
            withdrawals_usd=withdrawal,
        )
        closing = y.closing_usd
        assert closing >= 0, "Illustrative withdrawal exceeds available balance."
        rows.append(
            {
                "year_index": y.year,
                "opening_usd": y.opening_usd,
                "deposits_usd": y.deposits_usd,
                "return_rate": y.return_rate,
                "investment_return_usd": y.investment_return_usd,
                "withdrawals_usd": y.withdrawals_usd,
                "closing_usd": closing,
            }
        )
        opening = closing
    return rows


def fund_stress_scenarios() -> list[dict]:
    """Five-year synthetic fund paths. Values are not Guyana forecasts."""
    cases = {
        "illustrative_baseline": {
            "deposits": [4.0e9, 4.2e9, 4.4e9, 4.5e9, 4.5e9],
            "withdrawals": [2.0e9, 2.2e9, 2.4e9, 2.5e9, 2.5e9],
            "returns": [0.04] * 5,
        },
        "low_price_and_lower_deposits": {
            "deposits": [2.4e9, 2.1e9, 2.2e9, 2.5e9, 2.8e9],
            "withdrawals": [2.0e9, 2.0e9, 2.0e9, 2.0e9, 2.0e9],
            "returns": [0.03] * 5,
        },
        "higher_spending": {
            "deposits": [4.0e9, 4.2e9, 4.4e9, 4.5e9, 4.5e9],
            "withdrawals": [3.0e9, 3.3e9, 3.5e9, 3.7e9, 3.9e9],
            "returns": [0.04] * 5,
        },
        "market_loss_then_recovery": {
            "deposits": [4.0e9, 4.0e9, 4.0e9, 4.0e9, 4.0e9],
            "withdrawals": [2.0e9] * 5,
            "returns": [-0.10, 0.02, 0.06, 0.05, 0.04],
        },
    }
    rows: list[dict] = []
    for name, inputs in cases.items():
        path = fund_path(
            opening_usd=4.0e9,
            annual_deposits=inputs["deposits"],
            annual_withdrawals=inputs["withdrawals"],
            annual_returns=inputs["returns"],
        )
        for row in path:
            row["scenario"] = name
            rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        out = csv.DictWriter(handle, fieldnames=list(rows[0]))
        out.writeheader()
        out.writerows(rows)


def test_reconciliation() -> None:
    first = waterfall(100, 1, 0.02, 0.75, 0.75)
    assert round(first["government_total_usd"], 4) == 14.5
    assert round(first["government_share_of_gross"], 4) == 0.145
    assert round(first["contractor_profit_after_royalty_usd"], 4) == 10.5

    lower_cost = waterfall(100, 1, 0.02, 0.75, 0.20)
    assert round(lower_cost["government_total_usd"], 4) == 42.0
    assert lower_cost["government_total_usd"] > first["government_total_usd"]

    assert waterfall(0, 0, 0.02, 0.75, 0.75)["government_total_usd"] == 0

    p = fund_path(
        100.0,
        annual_deposits=[20.0, 20.0],
        annual_withdrawals=[10.0, 10.0],
        annual_returns=[0.0, 0.0],
    )
    assert p[0]["closing_usd"] == 110.0
    assert p[1]["opening_usd"] == 110.0
    assert p[1]["closing_usd"] == 120.0


if __name__ == "__main__":
    test_reconciliation()
    here = Path(__file__).resolve().parent

    contract_rows = contract_scenarios()
    write_csv(here / "ILLUSTRATIVE_SCENARIOS.csv", contract_rows)

    shock_rows = production_shock_scenarios()
    write_csv(here / "ILLUSTRATIVE_PRODUCTION_SHOCKS.csv", shock_rows)

    fund_rows = fund_stress_scenarios()
    write_csv(here / "ILLUSTRATIVE_FUND_STRESS.csv", fund_rows)

    print(
        "Tests passed. Wrote "
        f"{len(contract_rows)} contract rows, "
        f"{len(shock_rows)} production-shock rows and "
        f"{len(fund_rows)} fund-stress rows."
    )
