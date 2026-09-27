# Climate-data white paper: publication control record

Author: Ragunauth Ramsaroop
Date: 27 September 2026
GitHub edition: version 1.0 manuscript, draft PR #73
Separate downloadable publication: expanded version 1.1, 24-page PDF, editable DOCX, full Markdown, source register and JSON audit record.

## Content inspected

The draft GitHub research files comprise a main manuscript with twelve numbered source references and supporting technical appendices. An offline audit script tests reference continuity, three hypothetical cash-flow scenarios and financed-emissions arithmetic. The downloadable expanded edition contains approximately 9,069 words, fifteen numbered chapters, ten technical appendices and eighteen numbered references. The extra six references support material on ECB transition-plan evidence, EBA ESG-risk and scenario requirements, IEA transition-financing economics, and NGFS physical-risk model limitations.

**Important version distinction:** The expanded publication PDF/DOCX/Markdown delivered in the ChatGPT conversation is not byte-identical to the three text files in this GitHub draft. Publication and merging should not proceed until editors synchronise the expanded manuscript into this branch, inspect changes and regenerate the PDF. The downloadable package is the authoritative expanded 1.1 publication edition until then. Do not publish the shorter GitHub branch as edition 1.1.

## Controls completed on downloadable edition 1.1

- All eighteen numbered references exist in the manuscript's bibliography, and all are cited within the manuscript.
- Mathematical recomputation under the specified hypothetical assumptions: downside NPV -USD 3.657 million and IRR 4.39%; base NPV +USD 1.818 million and IRR 13.09%; upside NPV +USD 8.376 million and IRR 20.06%.
- Illustrative financed-emissions attribution totals 40,000 tCO2e. The decomposition from 40,000 to 36,000 reconciles with -4,000 tCO2e net change.
- A4 PDF has 24 pages, embedded fonts, selectable text, populated title/author metadata, six structured tables and two explanatory figures. Every page was rendered and visually reviewed. The static contents page covers the fifteen main chapters and ten appendices.
- No extracted text blocks exceed page bounds in the finished PDF. The PDF opens successfully and is not image-only.
- A source-register CSV and machine-readable JSON editorial/arithmetic audit record accompany the PDF and DOCX in the downloadable research ZIP.

These checks are author-directed editorial and computational controls. Passing them does not independently establish accuracy of third-party data or source publication metadata.

## Gates remaining before unqualified public release

1. Synchronise complete 1.1 Markdown, reference register and figures into this branch, and commit a reproducible PDF-generation pipeline.
2. Run the repository's Python audit in CI on the final synchronised branch and record the workflow run and results.
3. Assign an independent specialist to challenge citation accuracy, IFRS and EBA applicability, model assumptions, methods, and climate/nature claims.
4. Obtain any project-specific operating records and authorised permissions before presenting named-company performance as verified fact.
5. Seek a separately scoped independent assurance engagement if the publication is to claim external assurance or verified operating outcomes.
6. Merge and deploy only after owner approval. Verify the live website and academic indexing separately; neither is implied by this draft PR.

No affiliation with or endorsement by McKinsey & Company is represented. The six-page LinkedIn carousel screenshot was a starting question, not an accessible or reproduced source document.
