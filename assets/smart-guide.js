(()=>{
"use strict";
const $=s=>document.querySelector(s),esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let semanticPipe=null,llmEngine=null;
async function waitBrain(){if(window.RRBrain)return window.RRBrain;return new Promise((resolve,reject)=>{let n=0;const t=setInterval(()=>{if(window.RRBrain){clearInterval(t);resolve(window.RRBrain)}else if(++n>50){clearInterval(t);reject(Error("brain unavailable"))}},100)})}
function cards(rows){return rows.map(x=>'<a class="rr-smart-card" href="'+esc(x.url)+'"><span>'+esc(x.type||"Resource")+'</span><strong>'+esc(x.title)+'</strong><small>'+esc((x.description||"").slice(0,210))+'</small></a>').join("")}
async function run(){
 const q=$("#rr-smart-query").value.trim();if(!q)return;const brain=await waitBrain();$("#rr-smart-status").textContent="Searching the public site locally…";
 const rows=await brain.search(q,{limit:10}),intent=await brain.classify(q);
 $("#rr-smart-intent").textContent=intent.length?"Intent: "+intent.map(x=>x.intent).join(", "):"Intent: general research";
 $("#rr-smart-results").innerHTML=rows.length?cards(rows):'<p>No strong match found. Try a broader phrase.</p>';
 $("#rr-smart-status").textContent=rows.length+" relevant resources found.";
 window.rrTrack?.("smart_search",{result_count:rows.length,query_length:q.length})
}
$("#rr-smart-run").onclick=run;$("#rr-smart-query").addEventListener("keydown",e=>{if(e.key==="Enter")run()});
document.addEventListener("rrbrainready",async()=>{const h=await RRBrain.history();$("#rr-smart-history").innerHTML=h.slice(0,8).map(x=>'<a href="'+esc(x.url)+'">'+esc(x.title)+'</a>').join(" · ")||"No local history yet."});
$("#rr-smart-reset").onclick=async()=>{const b=await waitBrain();await b.reset();$("#rr-smart-history").textContent="Local learning reset.";window.rrTrack?.("smart_memory_reset")};

async function semantic(){
 const q=$("#rr-smart-query").value.trim();if(!q)return;
 const status=$("#rr-semantic-status");status.textContent="Loading the on-device semantic layer. First use downloads a compact query-embedding model.";
 try{
  await import("/assets/smart-search.js");
  const ranked=await window.RRSmartSearch.semanticSearch(q,{limit:10,onProgress:p=>{if(p?.message)status.textContent=p.message}});
  $("#rr-smart-results").innerHTML=ranked.length?cards(ranked):'<p>No semantic match found. Try a broader phrase.</p>';
  status.textContent="Hybrid semantic search complete on this device.";window.rrTrack?.("semantic_search_used",{candidate_count:ranked.length})
 }catch(e){status.textContent="Semantic mode could not start in this browser. Standard Smart Guide search still works.";console.warn(e)}
}
$("#rr-semantic-run").onclick=semantic;

async function localLLM(){
 const q=$("#rr-smart-query").value.trim();if(!q)return;
 const brain=await waitBrain(),status=$("#rr-local-ai-status"),out=$("#rr-local-ai-output");status.textContent="Preparing local AI. First use downloads a model and can take time.";out.textContent="";
 try{
   if(!("gpu" in navigator)){throw Error("WebGPU unavailable")}
   if(!llmEngine){
     const webllm=await import("https://esm.run/@mlc-ai/web-llm@0.2.85");
     llmEngine=await webllm.CreateMLCEngine("Qwen2.5-0.5B-Instruct-q4f16_1-MLC",{initProgressCallback:p=>status.textContent=p.text||("Loading "+Math.round((p.progress||0)*100)+"%")});
   }
   let ctx=[];try{await import("/assets/smart-search.js");const hits=await window.RRSmartSearch.semanticSearch(q,{limit:6,onProgress:p=>{if(p?.message)status.textContent=p.message}});ctx=hits.map((x,i)=>({n:i+1,title:x.title,url:x.url,description:x.description,type:x.type}))}catch{}
   if(!ctx.length)ctx=await brain.contextFor(q,6);
   const sourceText=ctx.map(x=>"["+x.n+"] "+x.title+"\nURL: "+x.url+"\n"+x.description).join("\n\n");
   status.textContent="Generating locally from the selected site sources.";
   const prompt="Answer the user's question using only the provided RR site sources. If the sources are insufficient, say so. Cite sources inline as [1], [2], etc. Do not invent facts.\n\nQUESTION:\n"+q+"\n\nSOURCES:\n"+sourceText;
   const res=await llmEngine.chat.completions.create({messages:[{role:"system",content:"You are a source-bounded research assistant for ragunauthramsaroop.com. Be concise, factual and transparent about uncertainty."},{role:"user",content:prompt}],temperature:0.2,max_tokens:500});
   out.textContent=res.choices?.[0]?.message?.content||"No answer returned.";
   $("#rr-local-sources").innerHTML=ctx.map(x=>'<a href="'+esc(x.url)+'">['+x.n+'] '+esc(x.title)+'</a>').join("<br>");
   status.textContent="Local answer complete. Verify the linked sources.";window.rrTrack?.("local_ai_used",{source_count:ctx.length})
 }catch(e){status.textContent=e.message==="WebGPU unavailable"?"Local LLM mode needs a browser with WebGPU. Smart Guide search and semantic mode remain available.":"Local AI did not start. Smart Guide search remains available.";console.warn(e)}
}
$("#rr-local-ai-run").onclick=localLLM;
})();