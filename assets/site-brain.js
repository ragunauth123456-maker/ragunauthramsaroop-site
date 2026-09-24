(()=>{
"use strict";
if(location.search.includes("embed=1")||document.documentElement.dataset.noBrain==="1"||window.__rrSiteBrainBooted)return;window.__rrSiteBrainBooted=true;
const loadScript=src=>new Promise((resolve,reject)=>{if(document.querySelector('script[src="'+src+'"]'))return resolve();const s=document.createElement('script');s.src=src;s.defer=true;s.onload=resolve;s.onerror=reject;document.head.appendChild(s)});
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const idle=fn=>("requestIdleCallback"in window?requestIdleCallback(fn,{timeout:1800}):setTimeout(fn,500));
let api=null;
async function historyGet(){try{return (await idbKeyval.get("rrBrainHistory"))||[]}catch{return[]}}
async function historySet(a){try{await idbKeyval.set("rrBrainHistory",a.slice(0,30))}catch{}}
async function remember(){
 const url=location.pathname;if(url==="/smart/"||url.startsWith("/search/"))return;
 const title=document.querySelector("h1")?.textContent.trim()||document.title;
 let h=await historyGet();h=h.filter(x=>x.url!==url);h.unshift({url,title,at:Date.now()});await historySet(h)
}
async function boot(){
 try{
  await Promise.all([loadScript("/assets/vendor/comlink-4.4.2.js"),loadScript("/assets/vendor/idb-keyval-6.3.0.js")]);
  const worker=new Worker("/assets/brain-worker.js",{name:"RR Site Brain"});
  api=Comlink.wrap(worker);await api.init();window.RRBrain={
   search:(q,o)=>api.search(q,o||{}),suggest:q=>api.suggest(q),recommend:c=>api.recommend(c||{}),classify:q=>api.classify(q),contextFor:(q,n)=>api.contextFor(q,n||6),
   history:historyGet,reset:async()=>{await idbKeyval.del("rrBrainHistory");await idbKeyval.del("rrBrainPrefs")}
  };
  await remember();await addSmartNav();await renderAdaptive();
  document.dispatchEvent(new CustomEvent("rrbrainready"));
 }catch(e){console.warn("RR Site Brain unavailable",e)}
}
async function addSmartNav(){
 const nav=document.querySelector(".rr-platform-nav");if(nav&&!nav.querySelector('[href="/smart/"]')){const a=document.createElement("a");a.href="/smart/";a.textContent="Smart Guide";a.dataset.brainLink="1";nav.insertBefore(a,nav.children[1]||null)}
 const top=document.querySelector(".topbar .nav");if(top&&!top.querySelector('[href="/smart/"]')&&top.children.length<8){const a=document.createElement("a");a.href="/smart/";a.textContent="Smart Guide";top.insertBefore(a,top.querySelector(".cta")||null)}
}
function pageContext(){
 const meta=document.querySelector('meta[name="description"]')?.content||"";
 const main=document.querySelector("main")?.innerText||document.body.innerText||"";
 return {url:location.pathname,title:document.querySelector("h1")?.textContent||document.title,description:meta,text:main.slice(0,2200)}
}
async function renderAdaptive(){
 if(location.pathname==="/smart/"||document.querySelector(".rr-smart-adaptive"))return;
 const h=await historyGet();let recommendations=[],intent=[];
 try{
  const mod=await import("/assets/smart-search.js");
  if(window.RRSmartSearch?.recommendAdaptive){
   recommendations=await window.RRSmartSearch.recommendAdaptive(location.pathname,h.slice(1,8).map(x=>x.url),5);
   const inferred=window.RRSmartSearch.intent?.([pageContext().title,pageContext().description].join(" "))||"general";
   if(inferred&&inferred!=="general")intent=[{intent:inferred,score:1}]
  }
 }catch{}
 if(!recommendations.length){const r=await api.recommend({...pageContext(),recent:h.slice(1,8)});recommendations=r?.recommendations||[];intent=r?.intent||[]}
 if(!recommendations.length)return;
 const main=document.querySelector("main .wrap")||document.querySelector("main");if(!main)return;
 const sec=document.createElement("section");sec.className="panel rr-smart-adaptive";
 const intentText=(intent||[]).slice(0,2).map(x=>x.intent).join(" + ");
 sec.innerHTML='<div class="rr-smart-kicker">RR Site Brain'+(intentText?' · '+esc(intentText):'')+'</div><h2>Recommended next</h2><p>Selected locally from this site using the page you are reading and recent pages on this device.</p><div class="rr-smart-grid">'+recommendations.slice(0,3).map(x=>'<a class="rr-smart-card" href="'+esc(x.url)+'"><span>'+esc(x.type||"Resource")+'</span><strong>'+esc(x.title)+'</strong><small>'+esc((x.description||"").slice(0,150))+'</small></a>').join("")+'</div><div class="actions"><a class="btn alt" href="/smart/">Open Smart Guide</a><button class="btn alt" type="button" data-rr-brain-reset>Reset local learning</button></div><p class="muted">No page text or browsing history leaves your browser through this feature.</p>';
 const related=main.querySelector(".rr-related,.rr-related-tools,.rr-supporting-evidence");
 if(related)related.insertAdjacentElement("afterend",sec);else main.appendChild(sec);
 const urls=recommendations.slice(0,3).map(x=>x.url).filter(x=>typeof x==="string"&&x.startsWith("/"));
 if(navigator.serviceWorker?.controller&&urls.length)navigator.serviceWorker.controller.postMessage({type:"RR_PREFETCH",urls});
 sec.querySelectorAll(".rr-smart-card").forEach(a=>a.addEventListener("click",()=>window.rrTrack?.("smart_recommendation_opened",{destination_type:a.querySelector("span")?.textContent||""})));
 sec.querySelector("[data-rr-brain-reset]").onclick=async e=>{await window.RRBrain.reset();e.currentTarget.textContent="Local learning reset";window.rrTrack?.("smart_memory_reset")}
}
idle(boot);
})();