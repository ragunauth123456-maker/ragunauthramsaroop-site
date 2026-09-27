# Technical appendices and reproducibility package
## Accompanies: From Climate Data to Durable Value (Ragunauth Ramsaroop, September 2026)

**Reproducibility classification:** The tables and numerical results below use hypothetical teaching inputs. None is a statement of any named bank's, mine's or investor's performance. Source references [1]-[12] are in the main manuscript.

# Appendix A. Data dictionary and minimum control record

The institution should establish a relational source register keyed by reporting entity, facility/asset, reporting period, unit of measure, source type, document identifier and approved data owner.

| Field | Unit/type | Source/owner | Material control |
| --- | --- | --- | --- |
| Reporting entity and consolidation method | text | Legal/finance | Reconcile to financial reporting perimeter. |
| Reporting year and data cut | ISO dates | Controller | Prevent period substitution. |
| Asset, site and borrower IDs | immutable identifiers | Operations/credit | Prevent duplicate records across systems. |
| Metered electricity | MWh | Meter/utility | Compare meter totals and invoices, identify own generation. |
| Diesel purchased and used | litres | Procurement/tank records | Opening stock + deliveries - closing stock = modelled use, investigate variances. |
| Generation by source | MWh | Plant SCADA | Reconcile hourly generation and load, record curtailment. |
| Emission factor | tCO2e/unit, vintage | GHG technical owner | Document geography, gas coverage, heating value, annual version. |
| Corporate gross GHG emissions | tCO2e by scope | Sustainability/controller | Distinguish direct, energy-indirect and value-chain boundaries. |
| Loan outstanding | currency/date | Core banking | Match approved point-in-time convention. |
| Attribution denominator | currency/date/method | Financial data owner | Validate correct PCAF asset-class method and EVIC where applicable. |
| Reported financed emissions | tCO2e and data-quality score | Portfolio analytics | Flag missing exposures, aggregation and revisions. |
| Hazard coordinates and scenario | geospatial/reference | Risk | Confirm site-level precision and material risk. |
| Revenue, opex, capex and hurdle rate | currency/period | Finance | Trace to ledger and approved investment case. |
| Community and ecology indicators | defined metric | ESG/community | Validate consultation, grievance and biodiversity records. |

Each record should retain raw evidence, transformation code or query, preparer identity, review approval, calculation date, method version and change history. Site coordinates and personal data need access controls; the public paper should not expose confidential maps or individual-level records.

# Appendix B. Explicit valuation model for a hypothetical remote power project

## B1. Decision and counterfactual

An imaginary remote industrial operation considers a hybrid renewable-plus-storage retrofit. Management compares the retrofit with a feasible continued-diesel option incorporating required generator maintenance and replacement. The investment horizon is twelve years and all amounts are in constant, illustrative USD millions. Cash flows are end-of-year except the initial outlay, which occurs at time zero. Annual net benefit is the change in operating cash flow after incremental recurring maintenance and lost/replaced diesel-system costs. Benefits are not independently attributed to carbon pricing or voluntary credits.

The model does not purport to estimate solar yield, carbon savings, the market cost of equipment or a company's financial returns. Those quantities must be populated from engineering, procurement and verified baseline records for a real project.

## B2. Model definition

Let C0 be investment outlay, Bt first-year net operating benefit, d annual benefit degradation, r nominally consistent real discount rate, R the year-eight replacement outlay and S end-year-twelve residual value. Year t cash flow is:

CF0 = -C0

CFt = B1 × (1-d)^(t-1) - (R if t=8 else 0) + (S if t=12 else 0)

NPV(r) = sum from t=0 to 12 of CFt/(1+r)^t.

The internal rate of return is the rate which sets NPV to zero if the root is economically meaningful. The base, downside and upside are author-selected scenarios, not model-calibrated probability intervals. Do not average them into an expected return without a justified scenario probability distribution.

## B3. Disclosed input table

| Parameter | Downside | Base | Upside |
| --- | ---: | ---: | ---: |
| Time-zero investment | $12.0m | $12.0m | $12.0m |
| Year-one net operating benefit | $1.6m | $2.2m | $2.8m |
| Annual benefit degradation | 1.0% | 0.5% | 0.25% |
| Real discount rate | 12% | 10% | 8% |
| Year-eight replacement expenditure | $3.2m | $2.5m | $2.0m |
| Year-twelve residual value | $0.5m | $1.0m | $1.5m |
| NPV | **-$3.657m** | **+$1.818m** | **+$8.376m** |
| Unlevered project IRR | **4.39%** | **13.09%** | **20.06%** |

The calculations include replacement outlays and residual value. They exclude unmodelled externalities, financing structure, taxes, working capital, penalties for lost production and any revenue attributed to unverified carbon credits. If those effects are material, replace the teaching model rather than adding superficial precision.

## B4. Reproducibility pseudocode

    cash_flows = [-capital]
    for year in range(1, 13):
        annual = first_year_benefit * (1 - degradation) ** (year - 1)
        replacement = replacement_cost if year == 8 else 0
        salvage = residual_value if year == 12 else 0
        cash_flows.append(annual - replacement + salvage)
    npv = sum(cf / (1 + discount_rate) ** year
              for year, cf in enumerate(cash_flows))

No external model, proprietary data or unspecified assumptions are necessary to reproduce this example.

## B5. The decision rather than the headline

The base-case NPV is positive, but the downside NPV is negative. Management therefore needs site-specific fuel-price sensitivity, reliability scenarios, demand trajectory, procurement bids, battery performance guarantees, interest-rate exposure, technical safety and community review before any capital commitment. If reliability has separate economic value, quantify the avoided downtime against measured historical exposure and exclude overlap already embedded in operating benefits.

## B6. Nonfinancial verification

At a real site, measured outcomes should include gross electricity and fuel use, operational Scope 1 and 2 emissions, production-normalised energy intensity, battery availability, grid or generator dependency, actual capital spending, outage hours and applicable land, water and biodiversity indicators. No net-present-value result establishes environmental performance.

# Appendix C. Financed emissions teaching ledger

## C1. Two imaginary borrowers

Corporate borrower A has eligible outstanding exposure of USD 40m, attribution denominator USD 200m and emissions of 150,000 tCO2e within the specified scope. Corporate borrower B has eligible outstanding exposure of USD 25m, attribution denominator USD 100m and specified emissions of 40,000 tCO2e. Applying a simplified attribution formula produces:

A = (40/200) × 150,000 = 30,000 tCO2e.  
B = (25/100) × 40,000 = 10,000 tCO2e.  
Total attributed financed emissions = 40,000 tCO2e.

These calculations are valid only as a hypothetical teaching illustration. A production report needs asset-class-specific PCAF eligibility, an appropriate EVIC/debt denominator where relevant, selected borrower Scope 1/2/3 coverage, consistent currency conversion, data-quality grades, overlap controls, treatment of managed assets and a defensible date convention [7,8].

## C2. Change bridge without misleading impact claims

Suppose the next year's hypothetical portfolio figure declines from 40,000 to 36,000 tCO2e. A reconciliation identifies five drivers:

| Change driver | tCO2e | What it means |
| --- | ---: | --- |
| Operational emissions reductions by continuing borrowers | -5,000 | Candidate real-economy change, subject to verification. |
| Portfolio loan exits and repayments | -10,000 | Accounting portfolio change; no proved borrower reduction. |
| New lending to other borrowers | +7,000 | Portfolio entry; no proved increase caused by the lender. |
| Foreign exchange and changed attribution denominator | +1,000 | Financial/attribution effect. |
| Revised data and estimation methodology | +3,000 | Measurement effect requiring disclosure. |
| Net change | -4,000 | Reconciles 40,000 opening to 36,000 closing. |

The net 10% decline in this illustrative inventory is not a 10% verified reduction in borrower emissions. Only the operational-change component is a candidate real-economy result, and even this requires consistent borrower boundaries and assurance of the underlying data.

# Appendix D. Physical-risk scenario and limitations

An illustrative flood-related facility has a stylised 10% annual chance of a USD 5m shutdown loss, giving a simple one-hazard expected annual loss of USD 0.5m if those assumptions hold. A proposed protection project reduces this assumed chance to 4%, implying an avoided expected loss of USD 0.3m each year before its maintenance and capital costs. This arithmetic illustrates a risk mechanism, not a calibrated probability, an insurance quote or an NGFS prediction.

To assess a real site: obtain geocoded asset and critical suppliers; identify acute and chronic perils; check flood maps, climate scenarios and the historic event record; test compound hazards and recovery capacity; estimate gross and insured losses; and compare adaptation options. Avoid adding expected-loss reductions and separately modelled avoided downtime if they describe the same underlying event. Uncertain tail losses and unavailable local records require ranges and clearly stated decision limits.

# Appendix E. Materiality and claims-control protocol

The following protocol should precede any externally communicated claim.

**Claims register.** Maintain a unique ID, precise words, owner, scope, materiality rationale, period, source evidence, transformation method, underlying financial ledger or measured environmental data, confidence, review status and approved publication location.

**Materiality.** Identify the target audience. Investor-focused IFRS materiality differs from frameworks which separately consider wider effects on people and ecosystems. Map both when applicable, rather than claiming they are interchangeable.

**Carbon.** Report gross emissions by scope, boundary, measured-estimated share, factor vintage, base year, methodology and material restatements. State separately the use of any credits and the treatment allowed by the applicable framework. Avoid "carbon neutral" or "net zero" claims without independently reviewed definitions and evidence.

**Economic value.** Distinguish total savings, incremental contribution margin, avoided loss, financial NPV and societal benefits. For claims of profitability, record financing, tax, replacement and decommissioning assumptions. Where benefits are forecast, use "scenario" or "estimate" rather than "achieved."

**Assurance.** Assemble a traceable evidence package and seek appropriately scoped independent assurance when required or intended. Cite ISSA 5000 correctly [10], but do not call internal editorial checking independent assurance.

**Publication corrections.** Assign a persistent version ID and correction log. State why data were restated, the affected periods, materiality, changed equations and whether assurance conclusions require amendment.

# Appendix F. Adversarial audit checklist

An independent reviewer should be able to answer the following without interviewing the author or relying on private oral explanations:

1. Is every material factual statement supported by a source whose publication date and population match the assertion?
2. Does the manuscript distinguish third-party analysis, standards, author interpretation and hypothetical examples?
3. Is the McKinsey material presented as the motivation rather than as endorsement, confidential access or reproduced proprietary research?
4. Are reporting periods and organizational, geographical, asset-class and emissions boundaries defined?
5. Are source records and calculation scripts reproducible from an immutable version?
6. Have unit conversions, currencies, inflation convention and discount-rate consistency been checked?
7. Do financial scenarios include material capital replacements, maintenance, decommissioning and adverse assumptions?
8. Are financed-emissions changes decomposed so portfolio reallocation is not misrepresented as underlying emissions reductions?
9. Are environmental, nature, worker and community safeguards distinct from economic benefit claims?
10. Are climate scenario results labelled conditional and appropriately uncertain?
11. Is any claim of verified, audited, assured, peer-reviewed or indexed status supported by a third-party record?
12. Are third-party copyright, sensitive client records, personal data and site-security information protected?
13. Is the standards update date correct, especially the December 2025 IFRS S2 changes effective from 2027?
14. Are mandatory national requirements separated from international standards and voluntary guidance?
15. Is the version control and correction mechanism operational?

**Review outcome categories:** PASS means supported and reproducible; CONDITIONAL means documented but limited by disclosed uncertainty or missing external data; FAIL means unsupported, internally inconsistent or materially misleading; NOT APPLICABLE means outside the stated scope. Passing a manuscript checklist is not an audit opinion.

# Appendix G. Evidence-to-claim matrix

| Manuscript claim | Main source | Nature of claim | Qualification |
| --- | --- | --- | --- |
| Sustainable-finance data may inform risk and client strategy | [1] | Industry analysis | Not evidence of a specific institution's realised profit. |
| 2026 total and clean-energy investment estimates | [2] | IEA global forecast | Not a 2026 audited total or country allocation. |
| 2025 carbon-pricing revenue and 2026 policy coverage | [3] | World Bank global statistics | Not an effective tax rate for an individual asset. |
| IFRS S1 investor-oriented disclosure requirements | [4] | International standard | Jurisdictional adoption must be checked. |
| IFRS S2 climate architecture | [5] | International standard | Read in conjunction with S1. |
| December 2025 S2 financed-emissions amendments | [6] | Published amendments | Effective periods start 1 January 2027. |
| Scope 3 Category 15 methodology | [7] | GHG Protocol guidance | Determine correct asset class and inventory scope. |
| Financial-industry financed-emissions accounting | [8] | PCAF/GHG Protocol standard resource | Check publication edition for reporting year. |
| Basel climate-risk management principles | [9] | Supervisory guidance | Proportionate and jurisdiction dependent. |
| Independent sustainability assurance methodology | [10] | International assurance standard | No assurance performed for this paper. |
| TNFD nature-related disclosures architecture | [11] | Voluntary recommendations | Not a global legal mandate. |
| Climate scenario design and use | [12] | NGFS guide | Scenarios are not predictions. |
| Positive base-case hypothetical NPV | Appendix B | Author arithmetic | Artificial inputs; no real company implication. |

# Appendix H. Open evidence gaps for any future company-specific study

Replace fictional operating assumptions with authorised fuel and electricity records, dispatch curves, validated emissions factors, procurement bids, battery warranty terms, financed debt and asset valuation records, third-party climate hazards, real observed pricing/fee changes, actual insurance provisions, verified local stakeholder outcomes and independent engineering/assurance review. Secure permission to publish any site-level or borrower information. Do not substitute a public sustainability press release for source-led verification.

**Auditability statement:** This manuscript is designed to invite scrutiny through transparent assumptions, reproducible examples, source provenance and explicit limitations. The absence of confidential operational data and independent external peer review prevents any claim of universal completeness, certified accuracy or independent audit.
