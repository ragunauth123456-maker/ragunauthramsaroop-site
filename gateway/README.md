# RR Research AI Gateway

This package adds an optional server-side reasoning layer for Ask Randy's Research.

The public website remains fully functional without this gateway. When the gateway is unavailable, disabled or rejected, the browser-side evidence assistant remains the fallback.

## Security model

The browser sends only:

```json
{"question":"...","mode":"general"}
```

The gateway then:

1. validates the allowed browser origin;
2. caps request size and question length;
3. applies a pilot per-instance request limit;
4. fetches the canonical public research index itself;
5. ranks the most relevant evidence;
6. sends only that evidence to the inference router;
7. requires structured JSON;
8. rejects source IDs outside the supplied evidence;
9. returns public source links with the answer;
10. falls back to evidence-only output if inference fails.

Provider credentials stay in server-side environment variables.

## Required environment variables

```
FREELLMAPI_BASE_URL=https://your-private-router.example/v1
FREELLMAPI_API_KEY=freellmapi-...
```

Optional:

```
FREELLMAPI_MODEL=auto:reliable
FREELLMAPI_TIMEOUT_MS=12000
RESEARCH_ALLOWED_ORIGIN=https://ragunauthramsaroop.com
RESEARCH_INDEX_URL=https://ragunauthramsaroop.com/assets/research-index.json
RESEARCH_GATEWAY_RPM=12
```

Do not commit real values.

## FreeLLMAPI role

The gateway expects the OpenAI-compatible FreeLLMAPI chat endpoint:

`POST /v1/chat/completions`

The default model is `auto:reliable`. This project treats FreeLLMAPI as a pilot inference layer because the upstream project describes itself as experimental rather than a production inference substrate.

## Browser activation

`assets/research-gateway-config.json` ships with `enabled: false`.

After deploying a tested gateway:

1. set `enabled` to `true`;
2. set `endpoint` to the public gateway endpoint;
3. update the Ask Research page Content Security Policy if the endpoint uses another origin;
4. run the website validation and browser tests;
5. verify live source-linked answers before enabling broad public traffic.

## Adapters

- `gateway/supabase/index.ts`: Supabase Edge Function adapter.
- `gateway/vercel/api/research/ask.mjs`: Vercel Node Function adapter.
- `gateway/research-ask.mjs`: portable core using Web APIs.

No backend has been deployed from this repository yet.
