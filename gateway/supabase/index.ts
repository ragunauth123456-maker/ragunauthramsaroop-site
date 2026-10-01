import { handleResearchRequest } from "../research-ask.mjs";

Deno.serve((request: Request) => handleResearchRequest(request, Deno.env.toObject()));
