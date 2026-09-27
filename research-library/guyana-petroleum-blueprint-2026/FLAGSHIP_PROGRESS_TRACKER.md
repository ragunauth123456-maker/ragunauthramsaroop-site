# CLOUD WORKER EXECUTION — 27 SEPTEMBER 2026

Three cloud-only GitHub Actions jobs are now installed on the research branch via `.github/workflows/guyana-edition2-cloud-workers.yml`, implemented in `edition2_cloud_workers.py`: (1) editorial/source-reference/duplicate review and editable manuscript packaging plus the existing fiscal and overall development tests, (2) HTTP source-link availability (NOT document-content or claim verification), and (3) two source-labelled SVG draft exhibits. **All three jobs passed** in live workflow run [36352095764](https://github.com/ragunauth123456-maker/ragunauthramsaroop-site/actions/runs/36352095764); rerun [36352446447](https://github.com/ragunauth123456-maker/ragunauthramsaroop-site/actions/runs/36352446447) passed after the three documented source-link repairs.

A separate **read-only, twice-weekly** scheduled workflow exists on default `main` at `.github/workflows/guyana-edition2-scheduled-workers.yml`: Monday and Thursday **11:23 UTC (07:23 Guyana)**, and manual dispatch. It checks out the research branch and executes the same jobs on GitHub-hosted runners. Its first push-triggered verification [36352122445](https://github.com/ragunauth123456-maker/ragunauthramsaroop-site/actions/runs/36352122445) passed across all three jobs. An ordinary research-branch manuscript/CSV/source change also triggers the parallel branch workflow. Each run uploads a 30-day artifact; no unattended AI manuscript writing is implied.

Current package audit (lexical regex): **62,800 core words**, distinct from earlier **66,605 whitespace-delimited words**. Neither count is a quality certificate; the threshold of 120,000 substantive original core words remains unmet. **141 registered source IDs**. The latest availability pass yielded 115 reachable URLs, 12 redirects not followed, 10 access blocked/rate-limited, 3 server/other outcomes and one HTTP 404 candidate (S71). HTTP availability is NOT authenticated-document verification. S105 and S135 updated to dated alternate links; original full-text 1993 World Bank S107 still requires accessible primary PDF. [#68](https://github.com/ragunauth123456-maker/ragunauthramsaroop-site/issues/68) and [#69](https://github.com/ragunauth123456-maker/ragunauthramsaroop-site/issues/69) track primary evidence recovery.

Four **manual-only** custom GitHub Copilot profiles were committed to `.github/agents/` on both `main` and the research branch: Guyana Evidence Researcher, Guyana Fiscal Auditor, Guyana Core Editor and Guyana Publication Engineer. **None is executing as a paid AI agent.** The connected GitHub app returned HTTP 403 when asked to assign Copilot; the owner must enable/authorize a paid Copilot cloud agent in GitHub UI if desired. Scoped, currently unassigned agent-ready editorial tasks are [#65](https://github.com/ragunauth123456-maker/ragunauthramsaroop-site/issues/65), [#66](https://github.com/ragunauth123456-maker/ragunauthramsaroop-site/issues/66), and [#67](https://github.com/ragunauth123456-maker/ragunauthramsaroop-site/issues/67).

**Edition 2 full PDF not built or published. PR #61 remains draft, issue #60 remains open. External peer review, remaining 53,395 words by earlier whitespace measure, source-to-claim verification, complete NRF H1 bridge, authoritative legal evidence and full visual QA remain release gates.**

---

# CURRENT EDITION 2.0 STATUS — 27 SEPTEMBER 2026

This status supersedes the historical word/source counts below. It was verified from the live ten integrated manuscripts and source register on the research branch, not inferred from the older Edition 1.2 PDF.

**Integrated core manuscript:** 66,605 whitespace-delimited words across ten Parts. Target 120,000–150,000 non-repetitive substantive core words before supporting annexes; minimum remaining 53,395 words. This is a quantitative measure, not proof that every paragraph has passed external substantive review.

| Part | Current integrated manuscript words |
|---|---:|
| I | 7,666 |
| II | 8,228 |
| III | 5,134 |
| IV | 7,059 |
| V | 7,649 |
| VI | 7,222 |
| VII | 6,572 |
| VIII | 4,905 |
| IX | 5,142 |
| X | 7,028 |

**Source register:** 141 entries (S01–S141). Registry count does not establish that all URLs are live, all citation pinpoints have been independently validated, or all source claims have passed legal/expert review.

**Structured datasets:** NRF annual stock-flow ledger, offshore project register, master chronology, local-content value-added framework, comparator mechanism matrix, public-investment delivery register, offshore environmental assurance matrix, PSA clause crosswalk, readiness checklist, governance RACI, and adverse-scenario playbook are in the research branch. Some are specification frameworks or contain unresolved source/reconciliation gaps, not completed audited datasets.

**Known material numerical blocker:** The H1 2026 NRF reconciliation is OPEN. Government receipts and fund accounting contain different cutoffs. Approximate USD 184.23 million difference between reported receipts and the rounded cash/IFRS stock-flow bridge has a plausible receivable-timing explanation but exact transaction mapping, accrual recognition and rounding remain to be proved. Treat as unresolved, not reconciled.

**PDF:** The latest built PDF remains Edition 1.2 and is an older publication candidate. Edition 2.0 has not been built or visually audited as a PDF. The Edition 1.2 CI release workflow has been switched to manual dispatch so automatic pushes do not make the old PDF appear newly completed.

**Remaining substantive work:** At least 53,395 additional non-repetitive core words; highest relative deficits currently Parts VIII–X and III/VII. Finish source-specific claim reviews, exact legal/source pinpoints, live URL checks, independent environmental/social evidence, NRF and public-investment reconciliation, quality original exhibits and maps, near-duplicate analysis, coherent cross-Part editing, Edition 2-specific CI, audited PDF build and visual QA.

**External peer review:** Pending. **Edition 2.0 final:** Not complete. **PR #61:** Draft. **Issue #60:** Open. No unattended book-writing agent or scheduled background process is claimed.

---

## HISTORICAL TRACKER ENTRIES (earlier milestones, not current live counts)

# FLAGSHIP PROGRESS TRACKER

Publication target: 520-560 substantive pages  
Working-PDF baseline: 56 pages  
Evidence cut-off: 27 September 2026  
Status legend: FOUNDATION, RESEARCHING, DRAFTED, SOURCE-AUDITED, MODEL-AUDITED, EXTERNAL-REVIEW, FINAL

| Part | Chapter | Target pages | Current status | Principal completion evidence |
|---|---:|---:|---|---|
| Front | Research method and executive material | 18 | FOUNDATION | Existing brief, source rules and review gates |
| I | 1. Guyana before offshore petroleum | 10 | RESEARCHING | Historical economic and institutional dataset |
| I | 2. A century of petroleum exploration | 10 | RESEARCHING | Exploration chronology and geological sources |
| I | 3. Environmental and natural-capital foundations | 10 | RESEARCHING | LCDS, forest, coastal and biodiversity baseline |
| I | 4. State-capacity baseline | 12 | RESEARCHING | Institutional map and statutory authorities |
| II | 5. Liza 2015 and the information shock | 10 | FOUNDATION | Existing chronology and operator/regulator sources |
| II | 6. The 2016 Stabroek agreement | 14 | FOUNDATION | Executed agreement plus clause crosswalk required |
| II | 7. Cost recovery and cost bank | 10 | FOUNDATION | Existing simplified model; full clause validation required |
| II | 8. Later model fiscal terms | 10 | FOUNDATION | Government model terms; agreement-level comparison required |
| II | 9. Contract governance for a newcomer | 8 | DRAFTED | Country playbook and newcomer blueprint |
| III | 10. Discovery to development decision | 10 | FOUNDATION | Development approval chronology required |
| III | 11. Pre-first-oil revenue institution | 12 | DRAFTED | 2019 NRF timing established; legal crosswalk incomplete |
| III | 12. First oil and first revenue cycle | 10 | FOUNDATION | Lift-to-cash reconciliation required |
| III | 13. FPSO-by-FPSO expansion | 10 | FOUNDATION | Production series and project table required |
| III | 14. Production data quality | 6 | DRAFTED | Existing definitions and audit rules |
| IV | 15. NRF law through time | 12 | RESEARCHING | 2019/2021/2024 statutes and crosswalk |
| IV | 16. Reconstructing fund cash flows | 12 | RESEARCHING | Annual reconciliation 2019-2026 H1 |
| IV | 17. Saving, spending and intergenerational equity | 10 | FOUNDATION | Comparative fiscal framework required |
| IV | 18. Non-oil primary balance and absorption | 10 | FOUNDATION | IMF and macro datasets required |
| IV | 19. Public investment management | 10 | FOUNDATION | Project register and outcome evidence required |
| IV | 20. National balance-sheet accounting | 8 | FOUNDATION | Wealth-accounting framework required |
| V | 21. Environmental authorization system | 10 | RESEARCHING | EPA statute, process and permit framework |
| V | 22. Project-by-project environmental evidence | 12 | RESEARCHING | Permit/EIA matrix per producing project |
| V | 23. Oil-spill preparedness and response | 12 | RESEARCHING | Statute, regulations, response capability and drills |
| V | 24. Liability, insurance and financial assurance | 12 | RESEARCHING | Court judgment and actual instruments required |
| V | 25. Coastal, fisheries and biodiversity exposure | 8 | FOUNDATION | Baseline and independent ecological evidence required |
| V | 26. LCDS, forest finance and petroleum | 10 | DRAFTED | Existing LCDS/carbon research to be re-verified |
| V | 27. Energy transition and emissions accounting | 6 | FOUNDATION | Boundary model and datasets required |
| VI | 28. Local content law and implementation | 10 | RESEARCHING | Statute and official programme data |
| VI | 29. Domestic value added versus procurement | 10 | FOUNDATION | Ownership/import/value-added sample required |
| VI | 30. Workforce and skills | 8 | FOUNDATION | Labour and training datasets required |
| VI | 31. Household welfare and distribution | 10 | RESEARCHING | Current-data availability audit required |
| VI | 32. Amerindian and hinterland development | 8 | RESEARCHING | Community-level and rights evidence required |
| VI | 33. Social licence, grievance and participation | 4 | FOUNDATION | Stakeholder and remedy documentation required |
| VII | 34. Growth beyond headline GDP | 8 | FOUNDATION | Oil/non-oil and welfare series |
| VII | 35. Infrastructure transformation | 10 | FOUNDATION | Project-level completion and lifecycle register |
| VII | 36. Energy security and gas-to-energy choices | 8 | FOUNDATION | Power project and system evidence |
| VII | 37. Private-sector development and diversification | 8 | FOUNDATION | Sector output, exports and productivity |
| VII | 38. Inflation, competitiveness and Dutch-disease channels | 8 | FOUNDATION | Price, wages, imports and tradables analysis |
| VIII | 39. EITI and extractive disclosure | 10 | RESEARCHING | 2026 validation record and historical reports |
| VIII | 40. Cost audits and revenue assurance | 10 | RESEARCHING | Audit status and dispute evidence |
| VIII | 41. Procurement and spending oversight | 8 | FOUNDATION | Procurement and audit evidence |
| VIII | 42. Parliament, judiciary and institutional checks | 10 | RESEARCHING | Statutes and authenticated decisions |
| VIII | 43. Statistical institutions and public data | 10 | FOUNDATION | Dataset coverage and quality audit |
| IX | 44. Norway | 10 | FOUNDATION | Fiscal framework and institutional context |
| IX | 45. Ghana | 8 | FOUNDATION | Revenue-management implementation evidence |
| IX | 46. Timor-Leste | 8 | FOUNDATION | Fund, budget and depletion evidence |
| IX | 47. Suriname | 8 | FOUNDATION | Pre-first-oil institutional evidence |
| IX | 48. Additional producer comparators | 8 | FOUNDATION | Comparator selection protocol required |
| IX | 49. Islands and small states | 6 | DRAFTED | Existing country playbook to expand |
| X | 50. Exploration-stage operating manual | 10 | DRAFTED | Country playbook |
| X | 51. Discovery-to-FID operating manual | 10 | DRAFTED | Country playbook |
| X | 52. First-oil readiness manual | 10 | DRAFTED | Country playbook |
| X | 53. Years 1-5 scale-up manual | 10 | DRAFTED | Country playbook |
| X | 54. Adverse scenarios and crisis playbooks | 10 | DRAFTED | Existing scenarios; model expansion required |
| Annex | Fiscal equations and model | 5 | FOUNDATION | Existing illustrative model |
| Annex | NRF accounting workbook | 5 | RESEARCHING | Reconciliation under construction |
| Annex | Environmental/spill audit checklist | 4 | DRAFTED | Existing review gates and blueprint |
| Annex | Contract review checklist | 4 | FOUNDATION | PSA clause extraction required |
| Annex | Local-content verification checklist | 3 | FOUNDATION | Data definitions required |
| Annex | Public-investment delivery checklist | 3 | FOUNDATION | Outcome framework required |
| Annex | Source-to-claim and corrections register | 6 | RESEARCHING | SOURCE_REGISTER.md active |

## Current quantitative baseline

- Working PDF: 56 pages.
- Existing 56-page working PDF research set at its earlier audit: 15,128 words.
- Current measured Markdown research package on this branch before integrated Parts VIII-X: 48,001 words.
- Source records embedded in the existing working PDF audit: 34.
- Current live branch source register: 86 records.
- Flagship target: 520-560 substantive pages.
- External peer review: pending.
- Final publication status: not complete.

## Immediate research priority

1. Complete Part I historical baseline.
2. Complete the 2016 PSA clause crosswalk.
3. Build year-by-year NRF reconciliation.
4. Build project-level permit/EIA register.
5. Obtain authenticated legal material for financial assurance and pollution-law status.
6. Expand local-content and social-outcome evidence.
7. Extend comparator dataset.
8. Rebuild the PDF only after substantive manuscript expansion, not as a page-count exercise.


## Measured branch expansion, 27 September 2026

The 520-560-page mandate has now been translated into ten research parts and technical workbooks.

Completed research-stage dossiers now exist for:
- Part I, pre-discovery foundations;
- Part II, contracts and cost recovery;
- Part III, pre-first-oil preparation and production;
- Part IV, NRF and national balance sheet;
- Part V, environment, spill risk and climate;
- Part VI, local content and social outcomes;
- Part VII, economic transformation;
- Part VIII, accountability and institutional learning;
- Part IX, international comparators;
- Part X, staged operating manual for new producers.

Technical work now also includes:
- NRF reconciliation workbook;
- environmental permit/risk register;
- model methods and limitations;
- expanded contract sensitivity scenarios;
- combined production shock scenarios;
- synthetic sovereign-fund stress scenarios.

Measured Markdown package before integrated Parts VIII-X: 48,001 words.
Integrated flagship Parts VIII-X added in this continuation: 6,179 words.
Current minimum measured research package: 54,180 words, excluding later duplicate-count reconciliation.
Live source register: 86 records.
Working PDF remains a preliminary edition and is not the flagship.
The final 520-560 substantive-page count will be measured only after complete manuscript integration, rendering, repetition audit and visual QA.


## Integrated flagship manuscript expansion

Integrated narrative manuscripts now exist for all ten flagship parts. Parts VIII-X were added after the 48,001-word branch measurement:

- Part VIII, Accountability and Institutional Learning: 2,083 words.
- Part IX, International Comparators and Transferability: 1,921 words.
- Part X, New-Producer Operating Manual: 2,175 words.
- Added integrated narrative: 6,179 words.
- Minimum current research package: 54,180 words before a full repository-wide de-duplication count.

These are substantive research-stage chapters, not page padding. The next PDF render must count actual pages only after integrating the new files and auditing repeated material.

## Edition 1.0 publication build

The flagship cloud build passed its PDF publication gate at 518 pages, 484 pages with at least 100 words, 86 source records, searchable text, and zero exact duplicate long paragraphs. The final source wording now treats remaining evidence items as future revision and external-review priorities rather than unpublished blockers. External peer review is not claimed.


## Adversarial audit status, 27 September 2026

Edition 1.0's former completion label has been superseded. Issue #60 is open and PR #61 is draft.

Edition 1.1 controls now include:
- 97-source register;
- high-risk claim-to-source matrix;
- Petroleum Activities Act 2023 legal addendum;
- audited NRF 2025 baseline;
- current EITI ongoing-status control;
- ICJ territorial/maritime-risk module;
- CORSIA and carbon-accounting boundaries;
- independent critical Indigenous/carbon-market perspective;
- redesigned scenario tables;
- primary TOC limited to major parts rather than granular analytical sections;
- publication_complete=false;
- external_peer_review=pending.

The publication remains an internally audited candidate until remaining legal, environmental, social and independent-review gates are evidenced.
