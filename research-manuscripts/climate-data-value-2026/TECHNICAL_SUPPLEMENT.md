# Technical supplement: reproducible examples, disclosure controls and independent challenge

Ragunauth Ramsaroop | Climate Data to Durable Value | September 2026 | Expanded research edition 1.1

This supplement forms part of the expanded manuscript and should be read with the primary source register and AUDIT_LOG.md. All numerical examples are fictional teaching cases. No named institution's project economics, actual financed emissions or operating performance have been verified in this study. Review and challenge of this paper are internal editorial procedures, not independent third-party assurance.

## A. Fictional twelve-year hybrid-power valuation

The comparison is a new solar-and-battery retrofit relative to continued diesel operations, under a hypothetical unchanged service demand. Upfront capital occurs at year zero, annual net benefit occurs at the end of each of years one through twelve, component replacement is incurred in year eight, and any residual value is received in year twelve. Benefits represent avoided recurring operating costs net of incremental recurring system expense. All amounts are constant USD millions and all discount rates are real. Taxes, debt financing, construction delays, working capital, decommissioning, carbon-credit sales and wider social externalities are excluded to maintain a reproducible teaching example.

| Input | Downside | Base | Upside |
|:--|--:|--:|--:|
| Time-zero capital, USD m | 12.0 | 12.0 | 12.0 |
| Year-one net benefit, USD m | 1.6 | 2.2 | 2.8 |
| Annual benefit degradation | 1.00% | 0.50% | 0.25% |
| Real discount rate | 12% | 10% | 8% |
| Year-eight replacement, USD m | 3.2 | 2.5 | 2.0 |
| Year-twelve residual, USD m | 0.5 | 1.0 | 1.5 |
| Resulting NPV, USD m | -3.657 | +1.818 | +8.376 |
| Unlevered IRR | 4.39% | 13.09% | 20.06% |

For each year t, cash flow equals first-year benefit × (1 - degradation)^(t - 1), minus the replacement expense if t = 8, plus residual if t = 12. NPV equals negative initial capital plus the sum of annual flows discounted using (1 + r)^t. IRR is the discount rate at which NPV equals zero. Run the dependency-free accompanying Python script for numerical assertions. These scenario labels express assumptions, not probability bounds. The hypothetical base case's positive NPV does not establish that a real solar-and-storage installation is profitable. A real investment requires metered hourly demand, independent technology engineering, dispatch optimisation, equipment procurement bids, fuel delivered cost, degradation warranties, power-system safety testing, legal review and real financing terms.

## B. Fictional financed-emissions attribution and decomposition

Assume an eligible corporate-borrower method with USD 40 million exposure, a USD 200 million attribution denominator and 150,000 tonnes of specified borrower emissions for borrower A. Its illustrative attributed inventory is 40/200 × 150,000 = 30,000 tonnes. Borrower B has USD 25 million exposure, a USD 100 million denominator and 40,000 tonnes, giving 25/100 × 40,000 = 10,000 tonnes. The two-exposure teaching inventory is 40,000 tonnes.

| Inventory driver | Change, tCO2e | Interpretation |
|:--|--:|:--|
| Opening attributed inventory | 40,000 | Fictional initial baseline |
| Continuing borrower operational reductions | -5,000 | Candidate real-economy effect, requiring evidence |
| Loan exits and repayments | -10,000 | Balance-sheet change; borrower emissions not necessarily lower |
| New financing | +7,000 | New attributed exposure |
| Foreign exchange and denominator change | +1,000 | Financial attribution effect |
| New source records and revised estimates | +3,000 | Measurement revision |
| Closing inventory | 36,000 | Ten-percent accounting reduction, not proven ten-percent physical abatement |

This formula is intentionally simplified. Production financed-emissions reporting requires the correct PCAF method for each asset class, the correct attribution denominator, stable measurement dates and currency conventions, borrower inventory boundaries, data quality and consistent consolidation. Avoid adding or subtracting avoided emissions and carbon credits from gross portfolio attribution unless the applicable reporting method expressly permits the presentation.

## C. Fictional flood-adaptation arithmetic

A fictional facility with a 10% annual probability of USD 5 million loss has a simplistic expected annual loss of USD 0.50 million. If an assumed adaptation action lowers that annual probability to 4%, expected annual loss becomes USD 0.20 million. The implied annual avoided loss is USD 0.30 million before cost. These probabilities are invented, not NGFS predictions or calibrated hazard estimates. A real appraisal must assess compound events, hazard data quality, asset-specific loss curves, insurance recoveries, deductibles, safety, climate scenario version and residual tail exposure. Do not count a prevented outage as both avoided operating loss and additional revenue.

## D. Fictional eight-year marginal-abatement-cost screen

Assume USD 2.0 million upfront investment, USD 0.32 million annual operating savings, 2,000 tonnes of hypothetical annual gross operational emissions avoided, an eight-year life and a 10% real discount rate. The capital recovery factor equals r / [1 - (1 + r)^(-n)] and equals approximately 0.18744 here. Annualised capital equals about USD 0.3749 million. Annual net expense is about USD 0.0549 million and the simple marginal abatement cost is around USD 27.4 per tonne. No discounting of emissions is assumed in this screen. It omits maintenance, financing structure, replacement and material nonfinancial impacts. When projects interact, calculate combined savings to avoid double-counting the same fuel reduction.

## E. Reproducible data dictionary

For each material source, register immutable source ID, legal entity, physical asset or borrower, owner, ISO reporting date, original unit, original currency, raw-source location, permitted use, reference framework, instrument factor vintage, transformation formula, reviewer, approval timestamp and version. Key records include purchased and consumed fuel; delivered electricity by source; production throughput; battery dispatch and availability; gross emissions by scope; loan exposure and reporting date; borrower emissions source and quality; attribution denominator; physical hazard map and resolution; site ecology and community-impact records; and public claim ID.

Reconcile diesel purchases with inventory movement and generator consumption. Reconcile MWh meters with bills and dispatch. Reconcile financial balances with the general ledger. Compare realised annual benefit with pre-approved counterfactual assumptions adjusted for throughput and weather. Maintain original evidence and material restatements. Protect borrower records and sensitive operational or grievance information from publication.

## F. Source-to-claim limits

The McKinsey 2026 analysis is practitioner context, not a randomised or representative causal study of profits. IEA 2026 investment numbers are forecasts of global sector spending. World Bank 2026 carbon-pricing figures concern global implemented policies and 2025 revenues. IFRS reporting standards are internationally issued but require local applicability checks. PCAF methods require the correct asset-class attribution and grade. Basel principles address prudential risk processes but are not a country-specific legal opinion. ISSA 5000 is an assurance framework; its publication does not assure this study. TNFD is a nature-disclosure framework, not a complete site-specific ecology assessment. NGFS pathways are conditional scenarios; the December 2025 model caveat requires attention when physical damages are assessed.

The January 2024 ECB assessment covers 95 banks and around 75% of euro-area loans. Its results should not be generalised to every global institution or reinterpreted as realised defaults. EBA risk-management guidelines began to apply in January 2026 to relevant EU institutions, with a one-year extension for small and non-complex banks; EBA environmental scenario guidelines begin January 2027. The October 2025 IEA transition-finance and September 2025 cost-of-capital publications offer sector and emerging-market context rather than individual-project verification.

## G. Public-claims gate and adversarial review

A public claim must provide its exact wording, reporting period, boundary, observational or modelled status, method, evidence owner, numeric uncertainty, reviewer, approval and publication version. Claims about achieved profit require realised accounting data and control for changing production. Claims about achieved climate impact require direct operational evidence. Financially attributed financed-emissions changes need a separate decomposition of borrower action, new loans, exited loans, valuation, currency and methodological revision. Claims about nature, biodiversity or community outcomes require separate primary records and a competent specialist review.

Before release, ask whether there are unsupported causal conclusions, missing material costs, unrecorded emissions estimates, incompatible accounting years, unsupported legal claims, failed model arithmetic, double counting, unlicensed source reuse or ambiguous assurance language. External review and substantive case verification remain open work. Track unresolved exceptions explicitly. The companion AUDIT_LOG.md records the checked public-source anchors and the script provides numerical reproducibility without proprietary data.
