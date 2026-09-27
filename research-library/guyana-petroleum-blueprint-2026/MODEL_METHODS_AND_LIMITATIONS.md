# MODEL METHODS AND LIMITATIONS

Working technical annex for the flagship Guyana petroleum case study.
Evidence cut-off: 27 September 2026.

## Purpose

The repository contains reproducible arithmetic for contract sensitivity, production shocks and sovereign-fund stress testing.

These models are decision aids. They are not forecasts of Guyana's petroleum revenue, operator returns, future production, future oil prices or future Natural Resource Fund balances.

## Contract waterfall

The simplified model uses five principal inputs:

- illustrative barrels;
- illustrative realized price;
- royalty fraction;
- cost-recovery ceiling;
- requested recoverable-cost fraction.

The model then calculates:

Gross sales = barrels x price.

Actual cost recovered = gross sales x the smaller of requested cost fraction and the cost-recovery ceiling.

Profit pool = gross sales - actual cost recovered.

Government profit oil = profit pool x illustrative government profit share.

Royalty = gross sales x royalty fraction.

Government total in the teaching model = government profit oil + royalty.

The current teaching implementation uses the published 2% royalty, 75% cost-recovery ceiling and equal residual profit split associated with the 2016 Stabroek agreement's public fiscal explanation. Contract-specific accounting, valuation, taxation, timing, recoverability, decommissioning and dispute provisions require clause-level review before any result is described as an actual entitlement.

## Why a percentage of gross sales is not a permanent government take

When recoverable costs use the full ceiling, the residual profit pool is smaller.

When actual recoverable costs fall below the ceiling, the residual profit pool is larger.

Later investment can add new recoverable costs.

For this reason, the 14.5% simplified binding-cap illustration should not be applied as a constant percentage across every field, month or development stage.

## Contract sensitivity dataset

ILLUSTRATIVE_SCENARIOS.csv contains 16 synthetic combinations:

- oil price: USD 40, 60, 80 and 100 per barrel;
- requested recoverable cost fraction: 20%, 50%, 65% and 75%;
- illustrative barrels: 10 million in each scenario.

The purpose is to show arithmetic sensitivity while holding volume constant.

No scenario is labelled as a Guyana forecast.

## Combined production shock dataset

ILLUSTRATIVE_PRODUCTION_SHOCKS.csv contains 18 synthetic combinations:

- production volume factor: 70%, 85% and 100% of an illustrative 10-million-barrel period;
- price: USD 40, 60 and 80;
- requested recoverable cost fraction: 50% and 75%.

This demonstrates that a price shock, production interruption and high cost recovery can occur together.

The cases are arithmetic stress tests. They do not estimate the probability of any operational outage.

## Sovereign-fund stress model

The fund model uses a simplified annual identity:

Closing balance = opening balance + deposits + illustrative investment return - withdrawals.

The return assumption is applied to the opening balance only.

Actual sovereign-fund performance depends on intra-year cash timing, portfolio weights, market values, realized/unrealized gains, expenses and accounting standards.

The synthetic fund cases are:

1. illustrative baseline;
2. lower deposits following a low-price condition;
3. higher spending;
4. market loss followed by recovery.

Each case begins with an illustrative USD 4 billion opening balance.

The figures deliberately do not reproduce the legal Guyana NRF withdrawal formula or predict actual future petroleum deposits.

## Why the fund model is separate from the NRF reconciliation

NRF_RECONCILIATION_WORKBOOK.md reconstructs observed historical public accounts.

ILLUSTRATIVE_FUND_STRESS.csv models hypothetical future paths.

Observed and hypothetical values must never appear in one chart without explicit labeling.

## Model review gates

Before the fiscal models enter the final flagship:

1. Extract the executed PSA's relevant fiscal and accounting clauses.
2. Review the accounting annex and valuation provisions.
3. Reconcile simplified formulas with actual petroleum entitlements.
4. Validate cost-bank treatment.
5. Separate royalty and profit-oil timing.
6. Review tax treatment.
7. Review decommissioning treatment.
8. Test unit consistency.
9. Test extreme cases and zero cases.
10. Obtain independent petroleum-fiscal review.

Before the fund model enters the final publication:

1. Reconcile audited annual NRF statements.
2. Verify statutory withdrawal rules by legal version.
3. Use transparent deposit assumptions.
4. Use transparent return assumptions.
5. Model liquidity separately from long-horizon return.
6. Include adverse market-return periods.
7. Include oil-price and production shocks.
8. Identify any public-debt interaction.
9. Identify disaster-related fiscal exposure.
10. Obtain independent public-finance review.

## Reproducibility

The source code is illustrative_model.py.

The generated datasets are:

- ILLUSTRATIVE_SCENARIOS.csv;
- ILLUSTRATIVE_PRODUCTION_SHOCKS.csv;
- ILLUSTRATIVE_FUND_STRESS.csv.

The final publication should record the Git commit associated with every model output and include a checksum manifest.

## Interpretation rule

A model result establishes only what follows from its stated assumptions.

It does not establish:
- future oil prices;
- future production;
- actual recoverable costs;
- future government receipts;
- optimal fiscal policy;
- expected spill loss;
- household welfare.

Any final decision statement must return to observed evidence, legal authority and disclosed assumptions.
