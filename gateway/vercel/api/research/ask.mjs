import { handleResearchRequest } from "../../research-ask.mjs";

export default async function handler(req, res) {
  const host = req.headers.host || "localhost";
  const protocol = String(req.headers["x-forwarded-proto"] || "https").split(",")[0].trim();
  const url = protocol + "://" + host + (req.url || "/api/research/ask");
  const headers = new Headers();
  for (const [key, value] of Object.entries(req.headers || {})) {
    if (Array.isArray(value)) value.forEach(item => headers.append(key, item));
    else if (value != null) headers.set(key, String(value));
  }
  let body;
  if (!["GET","HEAD"].includes(String(req.method || "GET").toUpperCase())) {
    body = typeof req.body === "string" ? req.body : JSON.stringify(req.body || {});
    headers.set("content-type","application/json");
  }
  const request = new Request(url,{method:req.method || "GET",headers,body});
  const response = await handleResearchRequest(request,process.env);
  res.statusCode = response.status;
  response.headers.forEach((value,key)=>res.setHeader(key,value));
  res.end(await response.text());
}
