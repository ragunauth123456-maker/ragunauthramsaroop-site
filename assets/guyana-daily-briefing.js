(()=>{
"use strict";
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let monitor={generated:"",sources:[]},live={generated:"",metrics:[]},sectorCfg={sectors:[]},researchQueue=[];

function guyanaDate(value){
  const d=new Date(value);
  if(!Number.isFinite(d.getTime())) return "Date unavailable";
  return new Intl.DateTimeFormat("en-GB",{timeZone:"America/Guyana",day:"2-digit",month:"short",year:"numeric",hour:"2-digit",minute:"2-digit",hour12:false,timeZoneName:"short"}).format(d);
}
function ageHours(value){
  const t=new Date(value).getTime();
  return Number.isFinite(t)?Math.max(0,(Date.now()-t)/3600000):Infinity;
}
function metricValue(item){
  const value=item&&item.value;
  if(typeof value==="string") return value;
  const n=Number(value);
  if(!Number.isFinite(n)) return "Not reported";
  if(item.unit==="USD"&&/GDP/i.test(item.label||"")) return "US$"+(n/1e9).toLocaleString(undefined,{maximumFractionDigits:2})+" bn";
  if(item.unit==="people") return n.toLocaleString(undefined,{maximumFractionDigits:0});
  if(item.unit==="%") return n.toLocaleString(undefined,{maximumFractionDigits:1})+"%";
  return n.toLocaleString(undefined,{maximumFractionDigits:2});
}
function sourceLookup(watch){
  return (monitor.sources||[]).find(s=>s.name===watch.match||s.name===watch.name||s.url===watch.url);
}
function sectorSignal(sector){
  const watched=(sector.watch||[]).map(w=>({watch:w,source:sourceLookup(w)}));
  const changed=watched.filter(x=>x.source&&x.source.changed);
  const monitored=watched.filter(x=>x.source);
  return {changed,monitored};
}
function latestRelevantMetrics(sector){
  const codes=new Set((sector.indicators||[]).map(x=>x.code));
  return (live.metrics||[]).filter(m=>m.indicator&&codes.has(m.indicator)).slice(0,2);
}
function renderFreshness(){
  const mg=monitor.generated,lg=live.generated;
  const newest=[mg,lg].filter(Boolean).sort((a,b)=>new Date(b)-new Date(a))[0];
  const oldestHours=Math.max(ageHours(mg),ageHours(lg));
  $("#brief-freshness").textContent=newest?guyanaDate(newest):"Source date unavailable";
  $("#brief-generated").textContent="Monitor: "+(mg?guyanaDate(mg):"unavailable")+" · Data: "+(lg?guyanaDate(lg):"unavailable");
  if(oldestHours>36){
    $("#brief-freshness-note").textContent="One or more source snapshots are older than 36 hours. Verify directly with the linked official sources before consequential use.";
  }
}
function renderTopline(){
  $("#brief-source-count").textContent=(monitor.sources||[]).length;
  $("#brief-change-count").textContent=(monitor.sources||[]).filter(x=>x.changed).length;
  $("#brief-indicator-count").textContent=(live.metrics||[]).length;
  $("#brief-sector-count").textContent=(sectorCfg.sectors||[]).length;
}
function renderSummary(){
  const sources=monitor.sources||[],changed=sources.filter(x=>x.changed),metrics=live.metrics||[];
  const changedNames=changed.map(x=>x.name);
  const stale=ageHours(monitor.generated)>36||ageHours(live.generated)>36;
  let text="The latest recorded monitor checked "+sources.length+" public sources and the headline snapshot contains "+metrics.length+" dated indicators. ";
  if(changed.length){
    text+=changed.length+" monitored source page"+(changed.length===1?" has":"s have")+" changed since the previous recorded run: "+changedNames.join(", ")+". ";
  }else{
    text+="No monitored page-content changes were detected in the latest recorded run. ";
  }
  text+=stale?"At least one snapshot is older than 36 hours, so direct source verification should take priority.":"The source and data snapshots are within the briefing freshness window.";
  $("#brief-executive-summary").textContent=text;
}
function renderSourceChanges(){
  const box=$("#brief-source-changes"),changed=(monitor.sources||[]).filter(x=>x.changed);
  if(!changed.length){
    box.innerHTML='<article class="source-card"><span>Latest monitor</span><h3>No monitored page-content change detected</h3><p>This means the monitored page hashes did not change since the prior recorded run. It does not establish that underlying conditions were unchanged.</p><a href="/observatory/">Review the full source watch →</a></article>';
    return;
  }
  box.innerHTML=changed.slice(0,9).map(x=>'<article class="source-card is-change"><span>'+esc(x.category||"Public source")+' · Change detected</span><h3>'+esc(x.name)+'</h3><p>'+esc(x.note||"Official public source.")+' Checked '+esc(guyanaDate(x.checked_at||monitor.generated))+'.</p><a href="'+esc(x.url)+'" target="_blank" rel="noopener noreferrer">Open source ↗</a></article>').join("");
}
function renderIndicators(){
  const preferred=["Exports (FOB)","Imports (CIF)","Monthly average exchange mid-rate","Real GDP growth","World Bank GDP growth","World Bank inflation","Population","World Bank GDP"];
  const rows=[...(live.metrics||[])].sort((a,b)=>{
    const ai=preferred.indexOf(a.label),bi=preferred.indexOf(b.label);
    return (ai<0?999:ai)-(bi<0?999:bi);
  }).slice(0,8);
  $("#brief-indicators").innerHTML=rows.length?rows.map(x=>'<article class="indicator-card"><span>'+esc(x.label)+'</span><strong>'+esc(metricValue(x))+'</strong><small>'+esc(x.unit||"published value")+' · '+esc(x.period||"period unavailable")+'</small><a href="'+esc(x.source||"#")+'" target="_blank" rel="noopener noreferrer">Source ↗</a></article>').join(""):'<article class="indicator-card"><span>Snapshot unavailable</span><strong>—</strong><small>No values have been estimated.</small></article>';
}
function renderSectors(){
  const box=$("#brief-sectors"),sectors=sectorCfg.sectors||[];
  box.innerHTML=sectors.map(sector=>{
    const signal=sectorSignal(sector),relevant=latestRelevantMetrics(sector);
    const state=signal.changed.length
      ? signal.changed.length+" monitored source page change"+(signal.changed.length===1?"":"s")+" detected"
      : signal.monitored.length
        ? signal.monitored.length+" monitored source"+(signal.monitored.length===1?"":"s")+" checked; no page change detected"
        : "Manual source verification required";
    const metricText=relevant.length?relevant.map(m=>m.label+": "+metricValue(m)+" ("+m.period+")").join(" · "):"Use the sector board for additional dated indicators.";
    return '<article class="sector-card"><span>'+esc(sector.label)+'</span><h3>'+esc(sector.label)+' decision watch</h3><p>'+esc(sector.summary)+'</p><div class="sector-state '+(signal.changed.length?"changed":"")+'">'+esc(state)+'</div><p><strong>Dated context:</strong> '+esc(metricText)+'</p><ol><li>'+esc((sector.questions||[])[0]||"Verify the key decision assumptions.")+'</li></ol><a href="/observatory/">Open sector board →</a></article>';
  }).join("");
}
function buildResearchQueue(){
  const sectors=sectorCfg.sectors||[];
  const changed=sectors.filter(s=>sectorSignal(s).changed.length);
  const chosen=changed.length?changed:sectors.filter(s=>["strategy","energy","mining"].includes(s.id));
  const seen=new Set(),rows=[];
  for(const sector of chosen){
    for(const item of sector.research||[]){
      if(seen.has(item.href)) continue;
      seen.add(item.href);
      rows.push({...item,sector:sector.label});
      if(rows.length>=6) break;
    }
    if(rows.length>=6) break;
  }
  researchQueue=rows;
  $("#brief-research").innerHTML=rows.map(x=>'<article class="research-card"><span>'+esc(x.sector)+'</span><h3>'+esc(x.label)+'</h3><p>Independent published research connected to the current sector watch.</p><a href="'+esc(x.href)+'">Open research →</a></article>').join("");
}
function briefingText(){
  const changed=(monitor.sources||[]).filter(x=>x.changed);
  const indicators=(live.metrics||[]).slice(0,8);
  const sectors=(sectorCfg.sectors||[]).filter(s=>sectorSignal(s).changed.length);
  return [
    "EXECUTIVE GUYANA BRIEFING",
    "Source monitor: "+(monitor.generated?guyanaDate(monitor.generated):"unavailable"),
    "Headline data: "+(live.generated?guyanaDate(live.generated):"unavailable"),
    "",
    "SOURCE WATCH",
    changed.length?changed.map(x=>"- Change detected: "+x.name+" ("+(x.category||"public source")+")").join("\n"):"- No monitored page-content changes detected in the latest recorded run.",
    "",
    "DATED HEADLINE INDICATORS",
    indicators.length?indicators.map(x=>"- "+x.label+": "+metricValue(x)+" · "+(x.period||"period unavailable")).join("\n"):"- No headline snapshot available.",
    "",
    "SECTOR ATTENTION",
    sectors.length?sectors.map(s=>"- "+s.label+": monitored page change detected; verify the source and decision implications.").join("\n"):"- No sector is elevated solely by page-change detection in the latest run.",
    "",
    "INTERPRETATION BOUNDARY",
    "Website page-change detection does not by itself establish a law, policy, market or institutional change. Verify consequential matters directly with the official source."
  ].join("\n");
}
function handoffSources(){
  const changed=(monitor.sources||[]).filter(x=>x.changed).map(x=>({label:x.name,href:x.url}));
  const research=researchQueue.map(x=>({label:x.label,href:x.href}));
  return changed.concat(research).slice(0,5);
}
function saveDecisionHandoff(){
  try{
    sessionStorage.setItem("rrResearchHandoff",JSON.stringify({
      question:"Executive Guyana Briefing decision review",
      answer:briefingText().slice(0,1800),
      sources:handoffSources(),
      mode:"guyana-briefing",
      createdAt:Date.now()
    }));
    return true;
  }catch(_){return false}
}
function bindActions(){
  $("#brief-print").onclick=()=>window.print();
  $("#brief-copy").onclick=async()=>{
    const button=$("#brief-copy");
    try{await navigator.clipboard.writeText(briefingText());button.textContent="Copied";setTimeout(()=>button.textContent="Copy briefing",1400)}
    catch(_){button.textContent="Copy unavailable";setTimeout(()=>button.textContent="Copy briefing",1600)}
  };
  $("#brief-ask").onclick=()=>{
    const changedSectors=(sectorCfg.sectors||[]).filter(s=>sectorSignal(s).changed.length).map(s=>s.label);
    const lens=changedSectors.length?changedSectors.join(", "):"national strategy, energy and mining";
    const question="What does the published research say decision-makers should examine in Guyana across "+lens+"?";
    try{sessionStorage.setItem("rrGuyanaQuestion",JSON.stringify({question,createdAt:Date.now()}))}catch(_){}
    location.href="/ask-research/?from=guyana";
  };
  $("#brief-executive").onclick=()=>{if(saveDecisionHandoff()) location.href="/tools/executive-brief-generator/?from=research"};
  $("#brief-decision").onclick=()=>{if(saveDecisionHandoff()) location.href="/decision-room/?from=briefing"};
  $("#brief-board").onclick=()=>{if(saveDecisionHandoff()) location.href="/tools/board-question-generator/?from=research"};
}
async function init(){
  try{
    const [m,l,s]=await Promise.all([
      fetch("/data/source-monitor.json",{cache:"no-cache"}).then(r=>{if(!r.ok)throw Error("source monitor");return r.json()}),
      fetch("/data/guyana-live.json",{cache:"no-cache"}).then(r=>{if(!r.ok)throw Error("headline data");return r.json()}),
      fetch("/assets/observatory-sector-briefs.json",{cache:"force-cache"}).then(r=>{if(!r.ok)throw Error("sector config");return r.json()})
    ]);
    monitor=m;live=l;sectorCfg=s;
    renderFreshness();renderTopline();renderSummary();renderSourceChanges();renderIndicators();renderSectors();buildResearchQueue();bindActions();
  }catch(error){
    $("#brief-freshness").textContent="Briefing data unavailable";
    $("#brief-executive-summary").textContent="The public briefing inputs could not be loaded. No values have been estimated. Use the Observatory and direct official-source links instead.";
    $("#brief-source-changes").innerHTML='<article class="source-card"><span>Unavailable</span><h3>Briefing inputs could not be loaded</h3><p>Open the Observatory or official sources directly.</p><a href="/observatory/">Open Observatory →</a></article>';
  }
}
init();
})();