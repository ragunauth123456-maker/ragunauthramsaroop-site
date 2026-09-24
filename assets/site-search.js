(()=>{
"use strict";
let docs=[],filter="All",semantic=false,pagefind=null,seq=0;
const q=s=>document.querySelector(s),esc=s=>String(s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const byUrl=()=>new Map(docs.map(x=>[x.url,x]));
async function loadPagefind(){if(pagefind)return pagefind;try{pagefind=await import("/pagefind/pagefind.js");await pagefind.init();return pagefind}catch{return null}}
function featured(){const urls=["/copilot/","/tools/","/resources/","/learning-paths/","/guyana-intelligence/","/scenario-lab/","/data-library/","/methodology/","/executive-profile/"];const m=byUrl();return urls.map(u=>m.get(u)).filter(Boolean)}
function fallback(term){const words=term.toLowerCase().split(/\s+/).filter(Boolean),rows=docs.filter(x=>filter==="All"||x.type===filter);return rows.map(x=>({x,s:words.reduce((n,w)=>n+((x.title+" "+x.description+" "+x.text).toLowerCase().includes(w)?1:0),0)})).filter(z=>z.s>0).sort((a,b)=>b.s-a.s).slice(0,48).map(z=>z.x)}
function cards(rows,label){q("#site-search-count").textContent=rows.length+label;q("#site-search-results").innerHTML=rows.map(x=>'<a class="card resource-card" href="'+esc(x.url)+'"><div class="resource-type">'+esc(x.type||"Public")+'</div><h3>'+esc(x.title)+'</h3><p>'+esc(x.description||x.excerpt||"Public resource")+'</p><span class="go">Open →</span></a>').join("")||'<div class="panel"><p>No results. Try broader terms.</p></div>'}
async function render(){
 const run=++seq,term=(q("#site-q")?.value||"").trim();if(!term){cards(featured()," featured starting points");return}
 q("#site-search-count").textContent=semantic?"Preparing semantic search…":"Searching…";
 if(semantic){
  try{
   await import("/assets/smart-search.js");
   const rows=await window.RRSmartSearch.semanticSearch(term,{limit:48,type:filter,onProgress:p=>{if(run===seq&&p?.status)q("#site-search-count").textContent=(p.message||p.status)}});
   if(run!==seq)return;cards(rows," semantic results · processed on this device");window.rrTrack?.("semantic_search_completed",{result_count:rows.length});
  }catch(e){if(run!==seq)return;cards(fallback(term)," results · lexical fallback");q("#semantic-status").textContent="Semantic mode was unavailable, so search used the local text index."}
  return;
 }
 const pf=await loadPagefind();if(run!==seq)return;
 if(pf){
  try{
   const r=await pf.search(term);const m=byUrl(),rows=[];
   for(const item of r.results.slice(0,100)){const data=await item.data(),url=new URL(data.url,location.origin).pathname,meta=m.get(url);if(filter!=="All"&&meta?.type!==filter)continue;rows.push(meta||{url,title:data.meta?.title||data.url,description:data.excerpt?.replace(/<[^>]+>/g," ")||"",type:"Public"});if(rows.length>=48)break}
   if(run!==seq)return;cards(rows," results · Pagefind index");return
  }catch{}
 }
 cards(fallback(term)," results");
}
fetch("/assets/search-index.json",{cache:"force-cache"}).then(r=>r.json()).then(j=>{docs=j.documents||[];const u=new URL(location.href);if(u.searchParams.get("q"))q("#site-q").value=u.searchParams.get("q");render()});
let timer;q("#site-q")?.addEventListener("input",()=>{clearTimeout(timer);timer=setTimeout(render,120)});
document.querySelectorAll("[data-search-filter]").forEach(b=>b.onclick=()=>{filter=b.dataset.searchFilter;document.querySelectorAll("[data-search-filter]").forEach(x=>x.classList.remove("is-active"));b.classList.add("is-active");render()});
q("#semantic-toggle")?.addEventListener("click",async e=>{semantic=!semantic;e.currentTarget.classList.toggle("is-active",semantic);e.currentTarget.textContent=semantic?"Semantic AI on":"Enable semantic AI";q("#semantic-status").textContent=semantic?"Questions are embedded and ranked on your device. The first use downloads a compact language model and browser caching handles later use.":"Standard search uses the local Pagefind index with no model download.";window.rrTrack?.("semantic_mode_toggled",{enabled:semantic});render()});
})();