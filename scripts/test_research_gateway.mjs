import assert from "node:assert/strict";
import fs from "node:fs";
import { handleResearchRequest } from "../gateway/research-ask.mjs";

const index=JSON.parse(fs.readFileSync(new URL("../assets/research-index.json",import.meta.url),"utf8"));
const allowedOrigin="https://ragunauthramsaroop.com";
const baseEnv={
  RESEARCH_ALLOWED_ORIGIN:allowedOrigin,
  RESEARCH_INDEX_URL:"https://ragunauthramsaroop.com/assets/research-index.json",
  FREELLMAPI_BASE_URL:"https://router.example/v1",
  FREELLMAPI_API_KEY:"freellmapi-test-key",
  FREELLMAPI_MODEL:"auto:reliable",
  RESEARCH_GATEWAY_RPM:"50"
};

function makeRequest(body,origin=allowedOrigin,extraHeaders={}){
  return new Request("https://ai.ragunauthramsaroop.com/v1/research/ask",{
    method:"POST",
    headers:{"content-type":"application/json","origin":origin,"x-forwarded-for":"192.0.2.10",...extraHeaders},
    body:typeof body==="string"?body:JSON.stringify(body)
  });
}

function indexResponse(){
  return new Response(JSON.stringify(index),{status:200,headers:{"content-type":"application/json"}});
}

async function successFetch(input,init={}){
  const url=String(input);
  if(url.includes("research-index.json")) return indexResponse();
  if(url==="https://router.example/v1/chat/completions"){
    assert.equal(init.headers.Authorization,"Bearer freellmapi-test-key");
    const payload=JSON.parse(init.body);
    assert.equal(payload.model,"auto:reliable");
    assert.equal(payload.response_format.type,"json_object");
    assert.match(payload.messages[0].content,/Answer only from the EVIDENCE/);
    return new Response(JSON.stringify({
      choices:[{message:{content:JSON.stringify({
        answer:"The published evidence separates measured electricity demand from development scenarios and examines generation, grid and reliability requirements through 2030.",
        citations:["S1"],
        confidence:"high"
      })}}]
    }),{status:200,headers:{"content-type":"application/json"}});
  }
  throw new Error("Unexpected fetch "+url);
}

async function invalidCitationFetch(input,init={}){
  const url=String(input);
  if(url.includes("research-index.json")) return indexResponse();
  if(url==="https://router.example/v1/chat/completions"){
    return new Response(JSON.stringify({
      choices:[{message:{content:JSON.stringify({
        answer:"This answer cites a source outside the supplied evidence and must not be accepted.",
        citations:["S99"],
        confidence:"high"
      })}}]
    }),{status:200,headers:{"content-type":"application/json"}});
  }
  throw new Error("Unexpected fetch "+url);
}

{
  const response=await handleResearchRequest(
    makeRequest({question:"What does the research say about Guyana electricity demand through 2030?",mode:"general"}),
    baseEnv,
    {fetch:successFetch}
  );
  assert.equal(response.status,200);
  assert.equal(response.headers.get("x-rr-mode"),"ai-evidence");
  const body=await response.json();
  assert.equal(body.ai_assisted,true);
  assert.equal(body.confidence,"high");
  assert.ok(body.sources.some(source=>source.href.includes("guyana-power-demand-2030")));
}

{
  let fetchCalled=false;
  const response=await handleResearchRequest(
    makeRequest({question:"Guyana power demand",mode:"general"},"https://evil.example"),
    baseEnv,
    {fetch:async()=>{fetchCalled=true;throw new Error("should not fetch")}}
  );
  assert.equal(response.status,403);
  assert.equal(fetchCalled,false);
}

{
  const response=await handleResearchRequest(
    makeRequest({question:"What does the research say about critical mineral supply chains?",mode:"board"}),
    baseEnv,
    {fetch:invalidCitationFetch}
  );
  assert.equal(response.status,200);
  assert.equal(response.headers.get("x-rr-mode"),"evidence-fallback");
  const body=await response.json();
  assert.equal(body.ai_assisted,false);
  assert.ok(body.sources.length>0);
  assert.ok(body.sources.every(source=>source.id!=="S99"));
}

{
  const env={...baseEnv,FREELLMAPI_BASE_URL:"",FREELLMAPI_API_KEY:""};
  let chatCalls=0;
  const response=await handleResearchRequest(
    makeRequest({question:"How does stakeholder trust relate to responsible mining?",mode:"institutional"}),
    env,
    {fetch:async(input)=>{
      const url=String(input);
      if(url.includes("research-index.json")) return indexResponse();
      chatCalls+=1;
      throw new Error("chat should not be called");
    }}
  );
  assert.equal(response.status,200);
  const body=await response.json();
  assert.equal(body.ai_assisted,false);
  assert.equal(chatCalls,0);
}

{
  const large=JSON.stringify({question:"Guyana energy",padding:"x".repeat(9000)});
  const response=await handleResearchRequest(makeRequest(large),baseEnv,{fetch:successFetch});
  assert.equal(response.status,413);
}

{
  const request=new Request("https://ai.ragunauthramsaroop.com/v1/research/ask",{
    method:"OPTIONS",
    headers:{origin:allowedOrigin}
  });
  const response=await handleResearchRequest(request,baseEnv,{fetch:successFetch});
  assert.equal(response.status,204);
  assert.equal(response.headers.get("access-control-allow-origin"),allowedOrigin);
}

console.log("PASS: research AI gateway grounding, origin, fallback, size and CORS controls");
