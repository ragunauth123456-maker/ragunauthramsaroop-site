# THE ACCOUNTABLE INVESTOR COMMUNICATION SYSTEM

## Artificial intelligence, information rights and institutional assurance

Ragunauth Ramsaroop | Volume 01 of *Ten Strategic Questions for the Next Decade* | Revised research manuscript, Part I | 27 September 2026

**Editorial stage: revised foundation manuscript.** This is a substantive rewrite of the executive opening and first chapters of the existing 17-page dossier. The intended full edition remains 120–160 substantive pages. External peer review, access to confidential investment-manager operating data and jurisdiction-specific legal review have not occurred. Do not describe this working manuscript as the finished flagship volume.

---

# Presidential and board-level decision brief

Investor communications are often treated as a production function: prepare a response, secure internal approval and deliver it by a contractual deadline. Artificial intelligence promises to reduce the time spent finding facts, comparing documents and producing the first draft. Yet the communication is not merely a document. It is the visible product of a chain of entitlements, internal decisions and operational controls. An apparently correct answer becomes an institutional failure when delivered to the wrong investor, based on an obsolete version of a valuation, released ahead of a permitted disclosure date or preserved without a complete approval record.

The central research question is therefore not the number of messages a model produces. It is whether an institution can deliver **more correct, permitted and recoverable answers per unit of review capacity**, without increasing the expected severity of confidentiality failures, misleading claims or missed escalations. The distinction is fundamental. A language model may draft a technically fluent answer and still select facts from a superseded fund report; a higher response count may coincide with an increasing number of unresolved corrections. Conversely, a well-controlled system may deliberately decline to answer a complicated question and generate an escalation record. Conventional productivity statistics would classify the second outcome as slower, even when the institution has prevented a material breach.

This study proposes the TRACE operating framework: **Triage, Retrieve, Attribute, Check and Escalate**. TRACE is an original analytic proposal, not an endorsed standard, legal safe harbor or field-validated model. Its purpose is to make every material response inspectable and to separate tasks suitable for automated assistance from decisions that remain with accountable professionals.

Three evidence boundaries govern the analysis. First, supervisory obligations are jurisdiction- and entity-specific. FINRA's 2026 oversight discussion says existing rules regarding supervision, communications, recordkeeping and fair dealing continue to apply to its member firms when they use generative AI; this does not automatically establish identical obligations for every global asset manager, private fund or sovereign institution [1]. Second, inaccurate marketing about AI itself creates a distinct problem: the U.S. SEC's March 2024 settled actions against two investment advisers concerned misleading statements about claimed AI capabilities, not demonstrated industry-wide investment-model misconduct [2]. Third, technical risk frameworks help organize testing but do not prove compliance. The NIST Generative AI Profile is voluntary, cross-sectoral guidance for managing generative-system risks and documenting evaluation [3].

A decision-ready institutional assessment should answer five questions:

1. Which investor, fund vehicle, document version, disclosure date and contractual entitlement authorize the proposed answer?
2. Which kinds of request can pass through a controlled retrieval-assisted workflow, and which require legal, compliance, investor-relations or portfolio-management decisions?
3. What independent evidence establishes response accuracy, authorized disclosure, complete retention and timely correction when the service is busy?
4. What happens after a model or retrieval error, supplier outage, revised valuation, compromised attachment or loss of a critical reviewer?
5. Does a fully burdened economic comparison show genuine incremental value once rework, review, integration, cybersecurity, incident response and opportunity cost are included?

# Chapter 1. The investor communication as a controlled decision

## 1.1 Define the unit of risk

The starting unit is not an email. It is one **communication case**, consisting of an authenticated request, a specific requester and entitlement profile, a declared purpose, one or more authorized source documents, an approval path, the released response and a preservation record. A conversation that receives three drafts, two revisions and one final approved reply remains one case for the purpose of measuring correct resolution. Otherwise, greater drafting activity appears to increase productivity without demonstrating delivery of an accurate result.

Cases should be categorized by consequence and reversibility rather than by superficial linguistic complexity. For example, a request for the published date of a previously distributed report differs materially from a request to interpret a side-letter liquidity right. The first may be answered through an approved public source and basic identity check. The second requires the correct executed agreement, applicable fund vehicle, investor identity, current governing terms and a qualified decision maker. A fluent paragraph generated from a similar but inapplicable side letter would be a failure even if every sentence sounded commercially plausible.

The firm should construct a communications inventory with at least these fields: product or fund, investor classification, domicile, distribution channel, information rights, request category, relevant documents, source version, privilege class, review owner, required approval sequence, release constraint, preservation schedule and correction mechanism. A source inventory without entitlements is inadequate, because the same document may be accurate while inaccessible to a particular investor.

## 1.2 Differentiate five decision layers

The first layer is **identity**: establish who is requesting information and on whose behalf. The second is **entitlement**: determine what the person is authorized to receive, for what purpose and during which period. The third is **source validity**: establish which signed, approved and current record controls the answer. The fourth is **substantive accuracy**: compare the resulting statement with the underlying record and reconcile contradictions. The fifth is **release authority**: determine who may approve delivery, whether an additional sign-off is required and how the institution records the final decision.

A machine-assisted workflow can assist with each layer, but assistance is not authorization. Identity verification requires approved credentials and procedures. Contract interpretation may involve disagreements among signed documents, fund terms, regulatory requirements and legal opinions. Financial explanations may rely on an effective-date valuation that was later revised. The firm should preserve the authority chain and disclose a meaningful uncertainty rather than allow generated text to resolve conflicts implicitly.

## 1.3 Design for the exception, not only the typical inquiry

Routine requests dominate many service workloads, yet rare cases may dominate total loss and reputational damage. A mean response-time benchmark conceals this distinction. Report response accuracy and release time by category, including unusual redemption queries, preferential information rights, complaints, fund restructuring events, sanctions restrictions and communications during revised financial reporting. Each classification requires a documented escalation rule and a designated owner.

The system should default to a safe holding response when the authorized source is missing, outdated or contradictory. A holding response is not a substitute for the contractual deadline or any legal duty to disclose, and it must be reviewed for the relevant jurisdiction. Its purpose is to prevent unsupported statements while a responsible professional determines the next step.

## 1.4 An evaluation design fit for a financial control

A pilot should compare the proposed operating method with an appropriately matched baseline. Relevant outputs include correctly resolved cases per 100 reviewer hours, time to final approved response, high-risk escalation recall, material correction rate, unauthorized retrieval incidents, preservation completeness and the time required to reconstruct an earlier answer. Report denominators and observation windows.

A simple before-and-after comparison may be distorted by easier case mix, changing markets, fewer staff absences or a new set of standardized templates. A stronger evaluation randomly assigns comparable, eligible low-risk cases to established and AI-assisted workflows, where legally and operationally appropriate. When randomized allocation is impractical, match by request type, investor segment, time of year, document availability and approval tier. Keep severe incidents as independently reported outcomes rather than hiding them inside an average speed or cost improvement.

The pilot must include a shadow period in which generated responses are compared with human-approved answers but are not sent externally. In later constrained release, holdout cases should remain available to detect time trends and reviewer learning. Record staff corrections and reversals: improving draft acceptance alongside declining reviewer scrutiny may represent increasing automation bias, not increasing accuracy.

# Chapter 2. TRACE: a proposed architecture of accountable assistance

## 2.1 Triage

Incoming content receives a case identifier and passes identity, attachment, information-right and risk-class checks before any broad retrieval. The intake engine identifies the fund vehicle, the requesting person's relationship to the vehicle, requested action and apparent urgency. It should never infer permission simply because two organizations have similar names or the requester previously received a different class of information.

Triage has at least three output paths. A routine route handles approved, previously released factual information. A controlled professional route handles substantive investor-specific financial interpretation or nonstandard requests. An exception route handles complaints, litigation holds, suspected fraud, account-compromise indicators, missing authorization, revised valuations and conflicting contracts. The class boundaries must be versioned; a material false-negative is a failure of supervision regardless of average classification accuracy.

## 2.2 Retrieve

Retrieval starts from a permission-filtered, approved corpus, not an unrestricted enterprise search. Document attributes include issuer, fund, execution status, effective date, approval owner, confidentiality class, version identifier and withdrawal status. Superseded material remains preserved for audit while disappearing from routine generation results. Unauthorized users must not obtain protected passages through broad semantic similarity, manipulated queries or summaries of retrieved sources.

Attachment text, incoming messages and retrieved public documents are untrusted content. Instructions within them must not override system rules, change information rights or initiate disclosure. This boundary should be tested with deliberately misleading and adversarial input.

## 2.3 Attribute

Every consequential numerical claim and interpretation should identify the approved source, document version, effective date and supporting passage. Merely attaching a citation does not establish correctness: the citation must support the precise claim, belong to the correct fund vehicle and be available to the intended recipient. When two approved sources disagree, attribution should surface the conflict rather than select the text that sounds most decisive.

The published response may provide references appropriate to the investor, while a protected internal record retains the full retrieval trace. The institution should determine which internal evidence can be retained without breaching privacy or privilege.

## 2.4 Check

Checks combine automated validation with clearly assigned human responsibility. Automated tests verify permitted recipient, source version, number consistency, prohibited language and completeness of required disclaimers. They cannot independently settle ambiguous legal rights or authorize market-sensitive releases. Professional reviewers should see the source passage alongside the proposed language, not only a polished generated draft. For material communications, use a second reviewer selected by documented independence criteria.

Testing must include negative cases: revoked investor access, cross-fund record overlap, a reporting-period mismatch, late valuation restatement and an attachment containing hostile instructions. Release criteria should be set in advance by the appropriate regulated entity rather than inferred from pilot results.

## 2.5 Escalate and recover

Escalation begins when the system cannot establish an authorized source, detects conflicting instructions or passes a predefined consequence threshold. An escalation record names an accountable person, a service deadline and the reason automatic progression stopped. Recovery covers more than correcting a single answer: identify all recipients who received affected content, whether the erroneous text was incorporated into later communications, who approved prior responses and what preservation or notification obligations follow.

An outage plan should provide a manual queue, bounded response categories, a documented restriction on unsupported financial interpretations and a supervisor-approved method for restarting systems after source integrity is re-established.

# Chapter 3. Regulation, institutional boundaries and contradictory evidence

FINRA's 2026 regulatory discussion explicitly treats generative-AI use as subject to member firms' existing obligations and identifies supervision, communications, recordkeeping and fair dealing as relevant. Its practical suggestions include governance frameworks, pre-deployment testing, continuous monitoring, prompt/output record consideration and model-version tracking. The operative requirement remains the applicable law and rule for the actual firm, not every example within a general oversight publication [1].

The SEC's 2024 settled enforcement actions against Delphia and Global Predictions illustrate a second category of risk: an institution's claims about its own AI sophistication may become misleading independently of whether an investor-facing model produces an incorrect reply. The two advisers agreed to a combined $400,000 in penalties without admitting or denying the SEC's findings. That outcome establishes the terms of the specific settled cases, not the prevalence of misrepresentation across all advisers [2].

Europe requires a separate legal lens. ESMA's May 2024 public statement addresses firms using AI for investment services provided to retail clients under MiFID II. ESMA identifies governance, transparency, quality, bias, privacy and overreliance concerns and stresses existing client-best-interest obligations. Its statement does not automatically cover each private fund investor correspondence flow or resolve the full EU AI Act classification of a particular application [4].

NIST AI RMF 1.0 and the July 2024 Generative AI Profile supply general risk-management vocabulary, including governance, evaluation, mapping and monitoring, without replacing jurisdiction-specific duties [3]. A globally deployed asset manager should therefore retain a legal obligations matrix by entity, product, customer, record type, geography and transaction. Common technical controls can be shared only after distinct legal and contractual requirements have been identified.

# Chapter 4. A falsifiable operating-economics model

The primary effectiveness quantity is **correctly resolved, permitted communication cases per 100 fully burdened reviewer hours**. Numerator cases must pass final quality and authorized-release checks. Denominator time includes source retrieval, drafting, legal/compliance review, correction, incident remediation, tooling administration and appropriate allocated oversight.

For an illustrative weekly queue, define cases arriving as A; routine share as r; average required reviewer hours for routine cases as h_r and for complex cases as h_c; and available reviewer hours as H. Required review effort is E = A[r·h_r + (1−r)·h_c]. Nominal unmet review effort is max(0, E−H). This effort backlog is not identical to unanswered case count and should not be presented as such without an explicit service discipline, case-mix assumption and queue model.

The earlier phase-one dossier uses **fictional** inputs A=250, r=0.78, h_r=0.35, h_c=1.8 and H=110. They give E=167.25 hours and a nominal 57.25-hour shortfall before rework or outages. These are arithmetic teaching values, not observed investment-manager statistics, regulatory benchmarks or estimated loss probabilities.

A publication-grade model should extend the basic effort equation to at least six features: arrival clustering near reporting deadlines; queue priority and contractual service deadlines; correlated reviewer absence; classification false negatives; rework following valuation changes; and a distinct severe-harm loss register. It should report confidence and uncertainty ranges only when the underlying empirical data support them. An institution-specific model requires de-identified case logs, task timings, measured quality outcomes, reviewer calendar availability, incident costs and a documented legal definition of an in-scope communication case.

# Chapter 5. First adversarial evidence tests

**Restated NAV with incomplete propagation.** A fund administrator delivers a revised quarter-end NAV after several approved answers have already been generated. Test whether the source index marks the prior version obsolete, pauses affected releases and identifies every previously sent message that incorporated the superseded value. The outcome is a reconstructable correction population, not a model's subjective confidence in the new figure.

**Conflicting investor rights.** Two investors have similar names but different executed side-letter terms. Test whether the information-right boundary is enforced before retrieval and whether a requester's prior access to one document can improperly authorize access to another. Include a case where a perfectly correct source extract is still prohibited for the intended recipient.

**Hostile attachment and human absence.** A credible-looking investor document contains instructions to export privileged information. The case arrives during a peak reporting week with the senior reviewer unavailable. Test the isolation of untrusted content, the fail-closed routing decision, protected logging and operation of the manual exception queue. A demonstration of one successful refusal does not establish safety against all future attacks.

**Silent productivity deterioration.** Draft completion time falls as reviewer time per case also decreases. A blind, independent sample finds rising errors in high-risk communications while aggregate volume and apparent acceptance rates improve. Test the governance process for pausing deployment and reporting the adverse trend without obscuring it through an average productivity metric.

# Research protocol: next substantive tranche

The immediate evidence acquisition phase should obtain de-identified case-class counts, actual reviewer-task times, document revision frequency, exception populations, permissible record-retention policies, cross-jurisdiction legal sign-off and vendor data-processing terms. Without this evidence, the manuscript can develop rigorous governance architecture and transparent hypothetical models but must not claim measured causal productivity gains or validated industry failure rates.

The full edition will add documented international comparisons, implementation case histories with demonstrable source access, alternative governance architectures, a reproducible queue simulation, legal mapping by relevant entity, a scenario-by-control effectiveness matrix, documented contradictory views and a separate unresolved-objections appendix. Each empirical claim will be reviewed against its source population and observation period.

## Source register for this revised foundation

[1] FINRA, **2026 Annual Regulatory Oversight Report: GenAI, Continuing and Emerging Trends** (report published December 2025). https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/gen-ai. Scope: FINRA member firms and FINRA regulatory context; the examples are not global legislation.

[2] U.S. Securities and Exchange Commission, **SEC Charges Two Investment Advisers with Making False and Misleading Statements About Their Use of Artificial Intelligence**, press release 2024-36, March 18, 2024. https://www.sec.gov/newsroom/press-releases/2024-36. Scope: two specific settled U.S. enforcement actions; no population prevalence inference.

[3] National Institute of Standards and Technology, **Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile**, NIST AI 600-1, July 26, 2024. https://doi.org/10.6028/NIST.AI.600-1. Scope: voluntary general technical guidance, not proof of entity-specific legal compliance.

[4] European Securities and Markets Authority, **Public Statement on AI and Investment Services**, ESMA35-335435667-5924, May 30, 2024. https://www.esma.europa.eu/document/public-statement-ai-and-investment-services. Scope: AI in MiFID II investment services provided to retail clients, with explicit attention to the existing applicable requirements.

© 2026 Ragunauth Ramsaroop. All Rights Reserved.
