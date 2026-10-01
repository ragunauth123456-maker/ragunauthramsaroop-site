(()=>{
"use strict";
const $=s=>document.querySelector(s);
const esc=s=>String(s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let cfg=null,monitor={sources:[]},current="mining",latest=[];

async function wb(def){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),7000);
  try{
    const url="https://api.worldbank.org/v2/country/GUY/indicator/"+encodeURIComponent(def.code)+"?format=json&per_page=8";
    const response=await fetch(url,{cache:"no-store",signal:controller.signal});
    if(!response.ok) throw new Error("HTTP "+response.status);
    const json=await response.json();
    const row=(json[1]||[]).find(x=>x.value!==null);
    if(!row) throw new Error("No published observation");
    return {...def,value:Number(row.value),year:row.date,source:"https://data.worldbank.org/indicator/"+def.code+"?locations=GY"};
  }finally{clearTimeout(timer)}
}
function fmt(item){
  if(item.code==="NY.GDP.MKTP.CD") return "US$"+(item.value/1e9).toLocaleString(undefined,{maximumFractionDigits:2})+" bn";
  return Number(item.value).toLocaleString(undefined,{maximumFractionDigits:item.digits});
}
function sourceState(w){
  const hit=(monitor.sources||[]).find(s=>s.name===w.match||s.url===w.url);
  if(!hit) return {label:"Manual verification",detail:"Open the official source for the latest position."};
  return {label:hit.status==="ok"?"Monitored source":"Check source",detail:"Last checked "+String(hit.checked_at||"pending").replace("T"," ").replace("+00:00"," UTC")};
}
function renderTabs(){
  $("#obs-sector-tabs").innerHTML=cfg.sectors.map(s=>'<button type="button" role="listitem" data-sector="'+esc(s.id)+'" class="'+(s.id===current?"is-active":"")+'">'+esc(s.label)+'</button>').join("");
  document.querySelectorAll("[data-sector]").forEach(b=>b.onclick=()=>{current=b.dataset.sector;renderTabs();renderSector()});
}
async function renderSector(){
  const sector=cfg.sectors.find(s=>s.id===current)||cfg.sectors[0];
  $("#obs-sector-title").textContent=sector.label+" briefing";
  $("#obs-sector-summary").textContent=sector.summary;
  $("#obs-sector-questions").innerHTML=sector.questions.map(q=>"<li>"+esc(q)+"</li>").join("");
  $("#obs-sector-sources").innerHTML=sector.watch.map(w=>{const st=sourceState(w);return '<a class="rr-sector-source" href="'+esc(w.url)+'" target="_blank" rel="noopener noreferrer"><strong>'+esc(w.name)+'</strong><small><span class="rr-source-state">'+esc(st.label)+'</span> · '+esc(st.detail)+'</small></a>'}).join("");
  $("#obs-sector-research").innerHTML=sector.research.map(r=>'<a class="rr-sector-research-link" href="'+esc(r.href)+'"><strong>'+esc(r.label)+'</strong></a>').join("");
  $("#obs-sector-scenario").href=sector.scenario||"/scenario-lab/";
  $("#obs-sector-status").textContent="Loading dated public indicators for "+sector.label+"…";
  $("#obs-sector-metrics").innerHTML='<article class="metric"><strong>Loading…</strong><span>Requesting public indicator data.</span></article>';
  const results=await Promise.allSettled(sector.indicators.map(wb));
  latest=results.filter(x=>x.status==="fulfilled").map(x=>x.value);
  $("#obs-sector-metrics").innerHTML=latest.length?latest.map(item=>'<article class="metric"><span>'+esc(item.label)+'</span><strong>'+esc(fmt(item))+'</strong><small>'+esc(item.unit)+' · observed '+esc(item.year)+'</small><a href="'+esc(item.source)+'" target="_blank" rel="noopener noreferrer">Official indicator ↗</a></article>').join(""):'<article class="metric"><strong>Source request unavailable</strong><span>No values were estimated. Open the official sources and Indicator Explorer.</span></article>';
  $("#obs-sector-status").textContent=latest.length?latest.length+" dated public indicators loaded. Missing series are not estimated.":"Live requests unavailable in this browser. Use the Indicator Explorer or official source links.";
  $("#obs-sector-ask").onclick=()=>handoffAsk(sector);
  $("#obs-sector-brief").onclick=()=>handoffBrief(sector);
}
function handoffAsk(sector){
  const q="What should decision-makers examine in Guyana's "+sector.label+" sector, using the published research and dated public-source evidence?";
  try{sessionStorage.setItem("rrGuyanaQuestion",JSON.stringify({question:q,createdAt:Date.now()}))}catch(e){}
  location.href="/ask-research/?from=guyana";
}
function handoffBrief(sector){
  const observations=latest.map(x=>x.label+": "+fmt(x)+" ("+x.year+", "+x.unit+")").join("\n");
  const sources=sector.watch.map(x=>({label:x.name,href:x.url})).concat(sector.research.map(x=>({label:x.label,href:x.href}))).slice(0,5);
  try{sessionStorage.setItem("rrResearchHandoff",JSON.stringify({
    question:"Assess current Guyana "+sector.label+" conditions and decision implications",
    answer:sector.summary+(observations?"\n\nLatest dated observations:\n"+observations:""),
    sources,
    mode:"observatory",
    createdAt:Date.now()
  }))}catch(e){}
  location.href=(sector.brief||"/tools/executive-brief-generator/")+"?from=research";
}
async function init(){
  try{
    const [c,m]=await Promise.all([
      fetch("/assets/observatory-sector-briefs.json",{cache:"force-cache"}).then(r=>{if(!r.ok)throw Error("config");return r.json()}),
      fetch("/data/source-monitor.json",{cache:"no-cache"}).then(r=>r.ok?r.json():{sources:[]}).catch(()=>({sources:[]}))
    ]);
    cfg=c;monitor=m;renderTabs();renderSector();
  }catch(e){
    const s=$("#obs-sector-status");if(s)s.textContent="Sector briefing configuration is unavailable. Use the Indicator Explorer and official-source watch below.";
  }
}
init();
})();