# Climate Data to Durable Value: research and numerical audit

Independent research audit log | 27 September 2026 | Expanded edition 1.1

## Scope and boundaries

This audit covers source provenance, selected quantitative statements, timing of major international standards, the distinction between emissions reporting and actual physical reductions, reproducibility of the fictional numerical cases, and representation of external assurance. It is an internal editorial and numerical review. It is not a statutory audit, academic peer review, third-party greenhouse-gas assurance or a legal opinion.

## Verified source anchors

- [McKinsey, 26 June 2026, updated July 2026](https://www.mckinsey.com/industries/financial-services/our-insights/turning-sustainability-from-regulatory-compliance-into-a-competitive-edge): practitioner analysis of financed-emissions information, underwriting, transition planning and client services. No claim of measured causal sector-wide returns.
- [IEA, World Energy Investment 2026](https://www.iea.org/reports/world-energy-investment-2026): estimated worldwide energy investment of USD 3.4 trillion in 2026, including USD 2.2 trillion for clean energy. Forecast, not realised audited spend or project return.
- [World Bank, State and Trends of Carbon Pricing 2026](https://www.worldbank.org/en/publication/state-and-trends-of-carbon-pricing): over 29% global emissions coverage and over USD 107 billion 2025 public revenues. Aggregates do not establish a uniform national carbon price.
- [IFRS S1](https://www.ifrs.org/issued-standards/ifrs-sustainability-standards-navigator/ifrs-s1-general-requirements/) and [IFRS S2](https://www.ifrs.org/issued-standards/ifrs-sustainability-standards-navigator/ifrs-s2-climate-related-disclosures/): issued June 2023; local mandatory adoption requires separate evidence.
- [December 2025 IFRS S2 amendments](https://www.ifrs.org/projects/completed-projects/2025/amendments-to-disclosure-of-greenhouse-gas-emissions-s2/): international effective reporting periods beginning 1 January 2027, early application permitted.
- [GHG Protocol Category 15 guidance](https://ghgprotocol.org/sites/default/files/standards/Scope3_Calculation_Guidance_0.pdf) and [PCAF/GHG Protocol resource](https://ghgprotocol.org/global-ghg-accounting-and-reporting-standard-financial-industry): relevant accounting methods; asset-class denominator, reporting year, source scope and data-quality treatment needed for production use.
- [Basel Committee climate-risk principles](https://www.bis.org/publications/202206-guidelines-principles-effective-management-and-supervision-climate-related-financial-risks): risk-control reference rather than automatically binding national law.
- [IAASB ISSA 5000](https://www.iaasb.org/publications/international-standard-sustainability-assurance-5000-general-requirements-sustainability-assurance): issued November 2024; international effective 15 December 2026, with jurisdictional adoption separate.
- [TNFD recommendations](https://tnfd.global/publication/recommendations-of-the-taskforce-on-nature-related-financial-disclosures/): September 2023 nature-related disclosure framework.
- [NGFS guide](https://www.ngfs.net/en/press-release/ngfs-publishes-updated-guide-climate-scenario-analysis) and [NGFS December 2025 limitations statement](https://www.ngfs.net/en/press-release/statement-regarding-physical-risk-estimates-phase-v-ngfs-long-term-scenarios): scenario design and qualified use of model results.
- [ECB study, January 2024](https://www.bankingsupervision.europa.eu/press/blog/2024/html/ssm.blog240123~5471c5f63e.en.html): 95 banks accounting for roughly 75% of euro-area loans; method-specific assessed transition exposure, not global default data.
- [EBA January 2025 management guidelines](https://eba.europa.eu/publications-and-media/press-releases/eba-publishes-its-final-guidelines-management-esg-risks): application from January 2026, with January 2027 extension for small and non-complex institutions; [environmental scenario guidelines](https://eba.europa.eu/publications-and-media/press-releases/eba-publishes-its-final-guidelines-environmental-scenario-analysis) apply January 2027.
- [IEA Transition Finance, October 2025](https://www.iea.org/reports/scaling-up-transition-finance) and [Cost of Capital Observatory, September 2025](https://www.iea.org/reports/cost-of-capital-observatory): background on financing transition projects and emerging-market capital costs.

## Arithmetic controls

Run \`python3 research-manuscripts/climate-data-value-2026/model_reproducibility.py\`. The three NPV and IRR results must agree with the manuscript's disclosed precision. The separate borrower attribution, financed-emissions bridge, flood-loss example and illustrative eight-year abatement-cost arithmetic must pass assertions.

## Adversarial review cases

1. Portfolio emissions decline solely because a loan leaves the balance sheet. Do not claim borrower decarbonisation.
2. Reported operational emissions decline due to lower production. Show throughput-adjusted results.
3. A source emission factor changes. Reconcile historical and current series before attributing the decline to operational intervention.
4. Savings exclude battery replacement, operations or decommissioning. Require complete lifecycle economics.
5. Climate scenario outputs include false precision or post-publication model caveats. Record scenario vintage and sensitivities.
6. Climate project affects nature, worker safety or community land access. Record independent impact and mitigation evidence.
7. Bank offers discounted financing while claiming commercial growth. Separate concession cost from fee income and risk change.
8. Global standards are presented as universally mandatory. Verify the specific legal perimeter and effective dates.
9. Unpublished McKinsey carousel is treated as primary research. Use the public article only, and attribute its claims.
10. Research is called externally assured or peer reviewed. No such engagement has been completed for this manuscript.

## Open controls before an externally assured edition

A qualified external reviewer must assess citation completeness and disciplinary interpretations; a jurisdiction-specific legal expert must confirm obligations for any named institution; project-specific economics require original bills, contracts and engineering; real company or borrower emissions require authorised records, correctly applied accounting methods and an appropriately scoped assurance engagement. All unresolved controls remain explicitly open.
