# GitHub Site Intelligence Forensic Audit

Date: 23 September 2026
Repository: ragunauth123456-maker/ragunauthramsaroop-site

## Objective

Identify active open-source projects, agent frameworks, browser intelligence libraries, search systems, quality tooling, security tooling, accessibility tooling, design skills, SEO skills and autonomous-agent resources relevant to a static GitHub Pages site. Separate public-browser components from local development agents so secrets and server credentials never enter the public bundle.

## Public runtime selected

| Project | GitHub signal at audit date | License | Use |
| --- | ---: | --- | --- |
| Pagefind/pagefind | 5,481 stars | MIT | Static, multilingual, low-bandwidth site search |
| oramasearch/orama | 10,561 stars | Apache-2.0 | Browser full-text, vector and hybrid retrieval |
| huggingface/transformers.js | 16,313 stars | Apache-2.0 | Build-time embeddings and optional browser query embeddings |
| GoogleChrome/web-vitals | 8,624 stars | Apache-2.0 | Patterns reviewed for performance telemetry |
| GoogleChrome/workbox | 13,023 stars | MIT | PWA patterns reviewed; the site retains a smaller custom service worker |

The live browser layer uses Pagefind plus an Orama hybrid index. The semantic index is built with Xenova/all-MiniLM-L6-v2 through Transformers.js and quantized to int8 for static delivery. Query embeddings run only after a visitor enables Semantic AI. Adaptive related-content ranking uses precomputed page embeddings and local browsing history.

## Local development intelligence selected

| Project | GitHub signal at audit date | License | Local role |
| --- | ---: | --- | --- |
| ruvnet/ruflo | 73,154 stars | MIT | Multi-agent harness, memory, agent definitions, skills and diagnostics |
| github/awesome-copilot | 39,322 stars | MIT | Agent instructions and web-development skills |
| anthropics/claude-plugins-official | 36,662 stars | Apache-2.0 | Official Claude plugin knowledge and skills |
| vercel-labs/agent-skills | 31,491 stars | repository license metadata not asserted by API | Web, frontend and optimization skills |
| coreyhaines31/marketingskills | 51,331 stars | MIT | SEO, CRO, analytics, copy and growth skills |
| addyosmani/web-quality-skills | 2,831 stars | MIT | Lighthouse, Core Web Vitals and web-quality skills |
| SawyerHood/dev-browser | 6,634 stars | MIT | Browser-driven development skill |
| superdesigndev/superdesign-skill | 599 stars | MIT | UI and design review skill |
| slowmist/slowmist-agent-security | 507 stars | MIT | Adversarial security-review skill |
| weAAAre/a11y-agents-kit | 32 stars | MIT | Accessibility agent resources |
| google/agents-cli | 5,985 stars | Apache-2.0 | Agent-development and evaluation skills |
| huggingface/upskill | 750 stars | Apache-2.0 | Skill generation and evaluation |

Ruflo 3.44.0 is installed locally. The site workspace contains 90 Ruflo agent definition files and more than 1,200 installed skill files across the Claude and Codex skill locations. Local agent folders are excluded from Git and are not deployed to GitHub Pages.

## Major frameworks audited but not placed in the public bundle

| Project | GitHub signal at audit date | Reason |
| --- | ---: | --- |
| microsoft/playwright | 96,573 stars | Used as an audit pattern and local browser test approach. No need to ship test automation to visitors. |
| mastra-ai/mastra | 28,290 stars | Strong server-side agent framework. Public static deployment would add backend and model-provider requirements. |
| vercel/ai | 26,922 stars | Strong TypeScript AI application toolkit. Public static use would still require a model path or exposed provider configuration. |
| langchain-ai/langgraphjs | 3,309 stars | Strong stateful agent-graph framework. More appropriate for a controlled backend than the current static deployment. |
| mlc-ai/web-llm | 19,174 stars | Browser LLM engine. Model downloads are materially larger than the semantic-search layer, so it is not loaded by default. |
| activepieces/activepieces | 24,700 stars | Workflow platform rather than a browser library for this static site. |
| reworkd/AgentGPT | 36,294 stars | Archived. |
| FlowiseAI/Flowise | 55,477 stars | Archived at audit date. |
| jameslittle230/stork | 2,760 stars | Older activity profile than Pagefind and Tinysearch. |
| tinysearch/tinysearch | 2,972 stars | Strong static-search alternative. Pagefind gives a better fit for the existing multilingual site. |

## Quality and security projects audited

GoogleChrome/lighthouse-ci, pa11y/pa11y-ci, dequelabs/axe-core, lycheeverse/lychee, gitleaks/gitleaks and ossf/scorecard were reviewed for QA and security patterns. The repository already contains Python validation, accessibility, performance and integrity checks. Ruflo security scanning was also run.

The initial Ruflo root scan reported hundreds of secret-pattern hits inside copied third-party agent skill examples. Those directories are local-only, ignored by Git and absent from the public site. A public dependency audit reported zero known npm vulnerabilities. Focused Ruflo scans of the public assets and tools returned no critical or high findings. Medium findings were generic innerHTML warnings. New smart-search, Copilot and recommendation output paths escape user-visible text before insertion.

## Smart-site architecture now present

1. Pagefind lexical index for fast static search.
2. Precomputed 384-dimensional semantic page embeddings.
3. Orama hybrid retrieval combining text and vector relevance.
4. Optional on-device query embeddings through Transformers.js.
5. Source-bounded Copilot with semantic retrieval and optional browser-local language-model synthesis where supported.
6. Adaptive next-resource recommendations using current-page context plus recent browser-local history.
7. Predictive prefetch of top recommended internal resources.
8. Service-worker caching for core intelligence assets.
9. Local browsing history only. No adaptive-history payload is uploaded by the site.
10. Local Ruflo agent harness for development, security review, testing, performance review and future maintenance automation.

## Boundaries

The live site does not hold model-provider API keys. Autonomous code-writing agents do not run inside the public browser. Public intelligence stays source-bounded and privacy-oriented. Code mutation remains a controlled development action rather than an unsupervised production-browser capability.


## Supplemental browser intelligence layer installed

A second lightweight retrieval path is installed to keep the site functional when semantic assets or optional model downloads are unavailable.

| Project | Version | License | Installed role |
| --- | --- | --- | --- |
| lucaong/minisearch | 7.2.0 | MIT | Fast browser-local full-text retrieval and intent fallback |
| GoogleChromeLabs/comlink | 4.4.2 | Apache-2.0 | Web Worker communication for the RR Site Brain |
| jakearchibald/idb-keyval | 6.3.0 | Apache-2.0 | Browser-local memory for recent-page learning |
| mlc-ai/web-llm | 0.2.85 | Apache-2.0 | Optional user-started local LLM mode on /smart/ only |
| huggingface/transformers.js | 4.3.0 | Apache-2.0 | Optional browser query embeddings plus build-time page embeddings |

The first three libraries are vendored locally under assets/vendor with license files. WebLLM is not loaded globally. It is requested only when a visitor selects the local-AI button and the browser supports WebGPU. Transformers.js query inference also starts only after Semantic AI is selected.

## Why some agent frameworks were not shipped to visitors

Browser-use, LangGraph.js, LangChain.js, Mastra and similar agent frameworks were reviewed. They are useful for controlled development or backend execution, but shipping autonomous code-writing or browser-control agents into a public static site would add unnecessary attack surface, model-provider configuration, or external execution requirements. The production browser layer therefore performs retrieval, ranking, local memory, source-bounded synthesis and prefetching, while code mutation and autonomous maintenance remain outside the public browser.

## Production intelligence paths

1. Pagefind provides static lexical retrieval.
2. Orama provides hybrid text/vector ranking against precomputed page embeddings.
3. Transformers.js creates query embeddings only after semantic mode is enabled.
4. MiniSearch provides an independent lexical fallback inside a Web Worker.
5. Comlink isolates search processing from the main page thread.
6. idb-keyval stores a short browser-local history for adaptive recommendations.
7. RR Site Brain chooses related resources from current-page context plus local history.
8. The service worker prefetches the top internal recommendations.
9. /smart/ exposes Smart Search, hybrid Semantic Search and an optional source-bounded WebLLM mode.
10. Ruflo remains local-only for development, testing, security review and agent orchestration.
