# Ask Randy's Research: AI pilot architecture

## Current release

The public assistant works without an external model. It searches the approved `assets/research-index.json` file in the visitor's browser, ranks matching evidence, returns concise evidence text and links to supporting pages.

This baseline provides three controls before generative inference is introduced:

1. Public-source grounding.
2. Visible source links.
3. No provider credential in browser code.

## FreeLLMAPI assessment

The upstream FreeLLMAPI project at https://github.com/tashfeenahmed/freellmapi provides an OpenAI-compatible router across multiple model providers. Its documented features include fallback routing, structured outputs, embeddings, model profiles, usage tracking and tool calling.

The upstream README also states that the project is for personal experimentation and learning rather than a stable production inference substrate. For this website, FreeLLMAPI should therefore serve as a pilot reasoning layer, not the only production dependency.

## Proposed pilot path

Public browser
-> same-origin research gateway
-> approved research retrieval
-> bounded prompt assembly
-> FreeLLMAPI pilot router
-> response validation
-> source-linked answer

The public browser never receives FreeLLMAPI provider credentials or upstream provider keys.

## Gateway contract

Suggested internal endpoint:

`POST /v1/research/ask`

Request:

```json
{
  "question": "What does the research say about Guyana power demand through 2030?",
  "mode": "general"
}
```

Response:

```json
{
  "answer": "Grounded answer text",
  "confidence": "high",
  "sources": [
    {
      "label": "Guyana Power Demand 2030",
      "href": "/white-papers/guyana-power-demand-2030/"
    }
  ],
  "model": "server-side metadata only"
}
```

## Security requirements

- Keep every provider key outside GitHub and browser JavaScript.
- Permit requests from the public site origin only.
- Apply request size limits, rate limits and abuse controls.
- Retrieve only from approved public website material.
- Exclude private email, private files and employer-confidential material.
- Treat retrieved documents as data, not executable instructions.
- Preserve source links in every grounded answer.
- Reject unsupported factual claims when retrieval evidence is weak.
- Keep provider and routing metadata out of normal public responses.
- Update the site's Content Security Policy only after the gateway hostname is confirmed.

## Quality gates before public generative mode

1. Build a benchmark set of at least 50 questions across Guyana, mining, ESG, energy, government relations, leadership, water, climate finance and AI infrastructure.
2. Compare browser-only answers against AI-assisted answers.
3. Require source correctness on every benchmark response.
4. Review hallucination rate, unsupported claims and citation mismatch.
5. Test prompt-injection resistance against untrusted page text.
6. Test rate limits and failure behavior.
7. Retain browser-only evidence search as fallback.

## Production transition

If the pilot improves answer quality, the same gateway contract should support a production inference provider without changing the public interface. FreeLLMAPI stays suitable for experimentation, fallback testing and model comparison.

No backend service, paid dependency or deployment credential is added by this document.
