# ADVERSARIAL PUBLICATION AUDIT
## Guyana's Petroleum Transformation, Edition 1.0
Audit date: 27 September 2026
Scope: content integrity, source traceability, numerical logic, legal status, PDF QA, publication controls and auditability.

## Audit conclusion

Edition 1.0 is a substantial research compendium, but it should not be represented as a fully closed, scrutiny-ready final publication yet.

The strongest parts are the documented chronology, separation of observed data from forecasts, the distinction between the 2016 Stabroek terms and later model terms, the Natural Resource Fund accounting framework, the transferability cautions, and the explicit effort to separate government, operator, multilateral and stakeholder positions.

The present release fails its own publication logic in several material areas. The failures are remediable. PR #61 has therefore been returned to draft and issue #60 reopened.

This audit is an internal adversarial review. It is not independent external peer review.

## Critical findings

### C1. Publication-status contradiction
The PDF cover describes a Flagship Reference Edition 1.0. The build audit marked `publication_complete: true`.

Yet the executive brief states that the final white paper is not externally reviewed or complete. The final page is titled "Open evidence items" and lists ten checks described as required before final publication. The publication review gates state: "No flagship release until each gate is evidenced." The progress tracker still contains many FOUNDATION and RESEARCHING statuses.

A publication cannot be both complete and incomplete under the same control framework.

Required correction:
- classify the current document as a publication candidate;
- set `publication_complete: false` until every mandatory gate is evidenced;
- preserve a separate internal-audit status and an external-review status.

### C2. The PDF page-count gate is materially overstated
Edition 1.0 has 518 rendered pages, but the total includes:
- 44 pages of table of contents;
- 3 pages of executive brief;
- 122 pages of integrated flagship manuscript;
- 185 pages of evidence dossiers and workbooks;
- 138 pages of technical annexes;
- 12 pages of scenario tables;
- 3 pages of publication review gates;
- 9 pages of source register;
- 1 page of open evidence items.

The builder's "substantive page" test used `len(text.split()) >= 100`. Dot leaders and fragmented tokens can inflate this count. A regex word audit found:
- median page density: about 154 words;
- 76 pages below 100 lexical words;
- integrated manuscript: 122 pages and about 25,600 lexical words.

The 518-page total remains a legitimate compendium length, but it is not equivalent to 518 pages of continuous core analysis.

Required correction:
- report total rendered pages and core analytical pages separately;
- exclude table of contents and source register from substantive-page claims;
- use lexical word counts;
- never use page count as a publication-quality proxy.

### C3. Architecture drift
The approved architecture contemplated roughly 54 core chapters. The typeset corpus contains 263 unique numbered chapter headings because research dossiers and operating workbooks were promoted into the same chapter hierarchy.

This weakens navigation and makes the work look more fragmented than the underlying research warrants.

Required correction:
- retain the 54-chapter core architecture;
- relabel supporting material as Annex, Evidence Note, Workbook or Checklist;
- keep supporting headings out of the main chapter numbering and primary TOC.

### C4. Source traceability is not strong enough for audit-grade publication
The source register contains 86 records. In the rendered PDF, 63 source IDs are cited at least once. In the 122-page integrated manuscript, 81 pages contain no source-ID marker.

A page without a source ID is not automatically unsupported, since some pages contain analytical method or guidance. The density nevertheless makes claim tracing slower than it should be for a publication intended to withstand legal, fiscal and technical challenge.

Required correction:
- create a source-to-claim matrix for every material factual claim;
- add page, section, table, paragraph or statutory provision pinpoints for Tier 1 sources;
- ensure every material number has source, observation date, unit and accounting boundary;
- distinguish primary evidence from attributed interpretation.

### C5. Several high-risk legal and regulatory gates remain open
The publication itself identifies these gaps:
- authenticated May 2026 Court of Appeal judgment not reviewed directly;
- commencement/implementing status of the 2025 oil-pollution statute not fully established;
- precise insurance, guarantee and financial-assurance instruments not fully reviewed;
- later cost-audit dispute outcomes remain unsettled.

Current external checks on 27 September 2026 confirm:
- EITI still lists Guyana's 2026 Validation as ongoing, not completed;
- Parliament and the Official Gazette establish enactment/publication of Act 6 of 2025;
- the available public government summary describes the May 2026 appellate result, but this audit has not located an authenticated full judgment;
- public petroleum sources continue to describe unresolved or ongoing cost-audit processes.

Required correction:
- do not characterize an unresolved legal point as settled;
- cite authenticated judgments and commencement instruments when found;
- label absence of a located public instrument as "not established in sources reviewed", not "does not exist".

### C6. Scenario tables fail the publication's readability gate
Pages 494-505 use wide CSV tables compressed into narrow portrait columns. Column labels break into fragments such as individual syllables and characters. This fails Gate 12's requirement that tables be readable at normal zoom.

Required correction:
- replace raw CSV dumps with grouped scenario tables;
- use human-readable labels;
- split fiscal, production and fund outputs into separate tables;
- add units, formula notes and scenario interpretation;
- preserve full CSV files as machine-readable supplements.

### C7. Accessibility is incomplete
The PDF is searchable and opens cleanly, but the document catalog does not expose a tagged PDF structure tree. The publication therefore does not satisfy a strong accessibility standard for semantic headings, table structure and figure alternative text.

Required correction:
- produce a tagged accessible PDF where feasible;
- ensure reading order, headings and table headers are encoded;
- add captions and text equivalents for material figures;
- run an accessibility check before public release.

### C8. External expert review is explicitly outstanding
The publication requires independent review across:
- petroleum fiscal economics;
- Guyana petroleum law and contract interpretation;
- public financial management;
- offshore environmental science and spill response;
- Indigenous/community safeguards;
- macroeconomics;
- data visualization and statistical interpretation.

No internal model review should be described as external review.

Required correction:
- keep external-review status pending;
- publish reviewer scope, conflicts policy and response-to-review log when reviews occur.

## Major coverage gaps or underdeveloped areas

### M1. Petroleum Activities Act 2023
The 2023 statutory framework should have an explicit chapter-level crosswalk showing what changed relative to the earlier legal framework and how the new Act interacts with legacy Stabroek rights, new licences, decommissioning, data, safety and regulation.

### M2. Maritime and geopolitical risk
A newcomer blueprint should address sovereign-boundary and maritime-security risk. Guyana's continuing case before the International Court of Justice concerning the 1899 Arbitral Award and related provisional measures is material contextual evidence. It should be presented neutrally, with no prediction of the merits outcome.

### M3. Latest NRF evidence
The Bank of Guyana now publishes audited NRF financial statements for 2025. These should be incorporated into the annual reconciliation before Edition 1.1 is treated as current through September 2026. Monthly 2026 NRF reporting should also be reconciled to the mid-year figures.

### M4. Forest-carbon market developments
The climate chapter should explicitly address CORSIA eligibility, corresponding adjustments, Article 6 accounting boundaries and competing views on Indigenous safeguards. Government programme claims, registry evidence and critical stakeholder analysis should remain distinguishable.

### M5. Independent social and Indigenous evidence
The current household evidence remains constrained by survey timing. The paper should deepen community-level evidence, including documented critical perspectives, without assuming either programme success or failure.

### M6. Local-content outcome measurement
Gross procurement is not domestic value added. Edition 1.1 should add a transparent bridge from gross spend to imports, wages, local ownership, retained profit, supplier capability and exportable capacity.

### M7. Project-level environmental performance
Permit and EIA existence is well documented. The harder audit question is performance:
- permit compliance;
- flaring and emissions;
- incident history;
- drill results;
- marine monitoring;
- independent sampling;
- financial-assurance enforceability.

The final publication should state where public data do not permit independent verification.

## PDF technical observations

Pass:
- file opens without encryption;
- 518 pages render successfully;
- searchable text is present;
- page numbering is consistent;
- no black-square glyph failures were found in the visual scan;
- fonts used for primary body text are embedded;
- source hyperlinks are present.

Needs correction:
- 44-page TOC is excessive;
- supporting material dominates the main hierarchy;
- scenario tables are unreadable in portrait format;
- PDF is not semantically tagged for accessibility;
- Helvetica is present as an unembedded Type 1 font in the file;
- publication metadata lacks a fuller keyword/version/rights package.

## Current evidence-status checks, 27 September 2026

1. EITI Validation: ongoing. EITI's current schedule still lists Guyana among ongoing Validations.
2. NRF 2025: audited statements are publicly available from the Bank of Guyana.
3. Oil Pollution Act 2025: enactment/publication established. Full operational commencement and implementing regulations require authoritative confirmation.
4. Court of Appeal financial-assurance case: government and press summaries are available. Authenticated judgment remains a required source for final legal characterization.
5. Cost audits: public records show material disputed costs and continuing resolution processes. Audit exceptions must not be reported as cash recovered.

## Edition 1.1 mandatory remediation plan

### Gate A: truth-in-publication controls
- change status from final/complete to publication candidate;
- remove contradictory completion claims;
- keep issue #60 open and PR #61 draft until mandatory gates pass.

### Gate B: source-to-claim audit
- produce claim IDs for all material numbers and legal propositions;
- add pinpoint references;
- validate all source URLs;
- add a corrections register.

### Gate C: legal hardening
- explicit Petroleum Activities Act 2023 crosswalk;
- authenticated appellate judgment if publicly obtainable;
- pollution-law commencement/regulations check;
- licence/permit version control.

### Gate D: financial hardening
- reconcile audited NRF 2020-2025;
- reconcile 2026 monthly reports through the evidence cut-off;
- connect lifts, receipts, deposits, returns and withdrawals without double counting;
- preserve cost-audit dispute status.

### Gate E: environmental and social hardening
- project-level compliance evidence;
- spill-response capability and financial assurance;
- independent Indigenous/community evidence;
- local-value-added bridge;
- current-data limitations prominently disclosed.

### Gate F: geopolitical and transferability hardening
- add maritime-boundary and territorial-dispute risk module;
- add institutional continuity and political-transition controls;
- keep political and electoral judgments out of the analysis.

### Gate G: PDF and data QA
- rebuild TOC around the core 54-chapter architecture;
- demote workbooks and evidence notes;
- redesign scenario tables;
- create accessible/tagged output where practical;
- separate total pages from core analytical pages;
- run link, citation, formula, metadata and visual checks.

### Gate H: external review
- independent expert reviews in the disciplines listed above;
- documented responses and unresolved-objection register;
- only then move from publication candidate to externally reviewed edition.

## Release rule

Edition 1.1 may be described as internally audited once Gates A-G pass.

It should not be described as independently peer reviewed, externally validated or immune from future correction unless the corresponding external evidence exists.

No publication can honestly be guaranteed to survive every conceivable criticism. The defensible standard is stronger: every material claim should be traceable, versioned, reproducible where quantitative, transparent about uncertainty and open to correction.


## Remediation status after Edition 1.1 rebuild

C1 Publication-status contradiction: REMEDIATED. Edition 1.1 is labelled an internally audited publication candidate. The audit record sets publication_complete=false and external_peer_review=pending.

C2 Page-count overstatement: REMEDIATED IN METRICS. Total rendered pages, lexical-density pages, core integrated pages and core lexical words are now reported separately. Page count is no longer used as proof of research quality.

C3 Architecture drift: REMEDIATED IN PRESENTATION. The ten-part structure remains primary. The 263 granular units are labelled analytical sections rather than chapters and are removed from the primary table of contents.

C4 Source traceability: PARTIALLY REMEDIATED. The source register has expanded from 86 to 97 records and a 45-item high-risk claim-to-source matrix has been added. Full sentence-level pinpoints remain a continuing editorial control.

C5 High-risk legal/regulatory evidence: OPEN. The paper uses narrow language where authenticated appellate text, commencement instruments, financial-assurance instruments or final dispute outcomes have not been established in public sources reviewed.

C6 Scenario-table readability: REMEDIATED. Wide raw CSV dumps have been replaced by six-column human-readable scenario tables while the full CSVs remain machine-readable supplements.

C7 Tagged-PDF accessibility: OPEN. Searchable text and reading order are present, but semantic PDF tagging is not claimed.

C8 External expert review: OPEN. No external peer-review claim will be made until specialist reviews and response logs are completed.

The internally audited candidate is therefore stronger than Edition 1.0, but the external-review and specified open-evidence gates remain visible rather than being masked by a completion label.
