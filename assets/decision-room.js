(()=>{
"use strict";

const FIELD_IDS=["title","owner","date","status","evidence-state","facts","unknowns","stakeholders","risks","options","criteria","recommendation","actions"];
const COUNT_IDS=["title","owner","date","facts","unknowns","stakeholders","risks","options","criteria","recommendation","actions"];
const STORAGE_KEY="rrDecisionRoomV2";
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let importedSources=[];

function value(id){return $("#dr-"+id)?.value?.trim()||""}
function setValue(id,v){const el=$("#dr-"+id);if(el&&v!=null) el.value=String(v)}
function state(){
  return Object.fromEntries(FIELD_IDS.map(id=>[id,value(id)]).concat([["sources",importedSources.slice(0,8)]]));
}
function safeSources(rows){
  return (Array.isArray(rows)?rows:[]).slice(0,8).map(x=>({
    label:String(x&&x.label||"Public source").slice(0,140),
    href:String(x&&x.href||"").slice(0,300)
  })).filter(x=>x.href.startsWith("/")||x.href.startsWith("https://"));
}
function lines(text){
  return String(text||"").split(/\n+/).map(x=>x.trim().replace(/^[-•*]\s*/,"")).filter(Boolean);
}
function appendField(id,text){
  const incoming=String(text||"").trim();
  if(!incoming)return;
  const current=value(id);
  setValue(id,current?current+"\n\n"+incoming:incoming);
}
function updateCompletion(){
  const count=COUNT_IDS.filter(id=>value(id)).length;
  $("#dr-completeness").textContent=count+"/"+COUNT_IDS.length+" fields populated";
}
function renderLedger(){
  const box=$("#dr-evidence-ledger");
  if(!box)return;
  if(!importedSources.length){
    box.innerHTML='<div class="dr-evidence-item"><strong>No imported sources yet</strong><small>Import a briefing or research context to preserve its public-source references here.</small></div>';
    return;
  }
  box.innerHTML=importedSources.map((s,i)=>{
    const attrs=s.href.startsWith("https://")?' target="_blank" rel="noopener noreferrer"':"";
    return '<div class="dr-evidence-item"><a href="'+esc(s.href)+'"'+attrs+'>'+esc(s.label)+'</a><small>Imported source '+(i+1)+'</small></div>';
  }).join("");
}
function save(){
  try{localStorage.setItem(STORAGE_KEY,JSON.stringify(state()))}catch(_){}
  updateCompletion();
}
function loadSaved(){
  try{
    const s=JSON.parse(localStorage.getItem(STORAGE_KEY)||"null");
    if(!s)return;
    FIELD_IDS.forEach(id=>setValue(id,s[id]||""));
    importedSources=safeSources(s.sources);
  }catch(_){}
  renderLedger();
  updateCompletion();
}
function handoffFromSession(){
  let direct=null,research=null;
  try{direct=JSON.parse(sessionStorage.getItem("rrDecisionRoomImport")||"null")}catch(_){}
  try{research=JSON.parse(sessionStorage.getItem("rrResearchHandoff")||"null")}catch(_){}
  const valid=x=>x&&x.createdAt&&Date.now()-Number(x.createdAt)<7200000;
  return valid(direct)?direct:valid(research)?research:null;
}
function importContext(){
  const x=handoffFromSession();
  if(!x){
    $("#dr-output-status").textContent="No recent context found";
    $("#dr-output-status").className="status next";
    return;
  }
  if(!value("title")) setValue("title",x.title||x.question||"Imported decision context");
  if(!value("status")) setValue("status","Explore");
  if(!value("evidence-state")) setValue("evidence-state","Partial");
  const context=String(x.answer||x.context||"").trim();
  if(context) appendField("facts",context);
  if(!value("criteria")) setValue("criteria","Evidence quality\nStrategic fit\nExecution feasibility\nRisk and downside exposure\nStakeholder and institutional impact\nReversibility");
  if(!value("unknowns")) setValue("unknowns","Confirm which imported statements remain assumptions, forecasts or interpretation rather than verified current facts.");
  importedSources=safeSources(x.sources);
  renderLedger();
  save();
  $("#dr-output-status").textContent=x.mode==="guyana-briefing"?"Imported Guyana Briefing":x.mode==="observatory"?"Imported Observatory":"Imported research context";
  $("#dr-output-status").className="status live";
}
function importScenario(){
  try{
    const x=JSON.parse(localStorage.getItem("rrLatestScenario")||"null");
    if(!x){$("#dr-output-status").textContent="No Scenario Lab case found";$("#dr-output-status").className="status next";return}
    const text=[
      "Scenario Lab snapshot: "+String(x.name||"Unnamed case"),
      "Fuel savings: "+Math.round(Number(x.fuelSavings)||0).toLocaleString()+" USD/year",
      "Post diesel emissions: "+Math.round(Number(x.postEmissions)||0).toLocaleString()+" tCO2e",
      "Local workforce: "+Number(x.localWorkforce||0).toFixed(1)+"%",
      "Local procurement: "+Number(x.localProc||0).toFixed(1)+"%"
    ].join("\n");
    appendField("facts",text);
    if(!value("title"))setValue("title","Review Scenario Lab case: "+String(x.name||"scenario"));
    save();
    $("#dr-output-status").textContent="Scenario imported";
    $("#dr-output-status").className="status live";
  }catch(_){
    $("#dr-output-status").textContent="Scenario import unavailable";
    $("#dr-output-status").className="status next";
  }
}
function topicQuestions(s){
  const text=[s.title,s.facts,s.risks,s.options,s.recommendation].join(" ").toLowerCase();
  const q=[
    "What exact decision is required now, and what is explicitly outside scope?",
    "Which verified fact would materially change the recommendation if it proved wrong?",
    "Which assumption carries the greatest downside if it is not resolved before approval?",
    "Which stakeholder, regulator or approval authority could materially change execution?",
    "What are the pause, escalation or exit triggers after the decision is taken?"
  ];
  if(/energy|power|electric|solar|renewable|battery|grid/.test(text))q.push("What reliability, demand, grid, fuel-price and storage assumptions drive the energy case?");
  if(/mining|mineral|gold|mine|geolog/.test(text))q.push("Which mineral-rights, environmental, infrastructure and community dependencies are on the critical path?");
  if(/investment|capital|finance|return|cost|budget/.test(text))q.push("What downside case has been tested, and which commitment becomes hardest to reverse after capital is deployed?");
  if(/environment|climate|carbon|water|biodiversity|esg/.test(text))q.push("Which environmental or ESG claims have a dated measurement basis and accountable owner?");
  if(/government|regulat|permit|institution|public/.test(text))q.push("Which institutional mandate, permit or regulatory interpretation requires direct verification before approval?");
  if(/community|stakeholder|social|grievance|local content/.test(text))q.push("How are affected stakeholders represented in the evidence, and what unresolved commitment could undermine execution?");
  return q.slice(0,8);
}
function sourceHtml(sources){
  if(!sources.length)return '<p>No public sources were imported into this pack.</p>';
  return '<div class="dr-source-list">'+sources.map(s=>{
    const attrs=s.href.startsWith("https://")?' target="_blank" rel="noopener noreferrer"':"";
    return '<a href="'+esc(s.href)+'"'+attrs+'>'+esc(s.label)+'</a>';
  }).join("")+'</div>';
}
function section(title,text){
  return '<h3>'+esc(title)+'</h3><p>'+esc(text||"Not yet recorded").replace(/\n/g,"<br>")+'</p>';
}
function build(pack=state()){
  const unknowns=lines(pack.unknowns),questions=topicQuestions(pack),sources=safeSources(pack.sources);
  const populated=COUNT_IDS.filter(id=>String(pack[id]||"").trim()).length;
  const html=[
    '<div class="method-meta">Decision record · '+esc(new Date().toLocaleString())+'</div>',
    '<h2>'+esc(pack.title||"Untitled decision")+'</h2>',
    '<div class="dr-pack-meta">',
      '<div><span>Owner</span><strong>'+esc(pack.owner||"Not assigned")+'</strong></div>',
      '<div><span>Target date</span><strong>'+esc(pack.date||"Not set")+'</strong></div>',
      '<div><span>Stage</span><strong>'+esc(pack.status||"Explore")+'</strong></div>',
      '<div><span>Evidence state</span><strong>'+esc(pack["evidence-state"]||"Exploratory")+'</strong></div>',
    '</div>',
    '<div class="dr-pack-grid">',
      '<div class="dr-pack-box">'+section("Verified facts",pack.facts)+'</div>',
      '<div class="dr-pack-box">'+section("Unknowns and assumptions",pack.unknowns)+'</div>',
      '<div class="dr-pack-box">'+section("Stakeholders",pack.stakeholders)+'</div>',
      '<div class="dr-pack-box">'+section("Principal risks",pack.risks)+'</div>',
      '<div class="dr-pack-box">'+section("Options under consideration",pack.options)+'</div>',
      '<div class="dr-pack-box">'+section("Decision criteria",pack.criteria)+'</div>',
    '</div>',
    section("Working recommendation",pack.recommendation),
    section("Immediate actions",pack.actions),
    '<h3>Unresolved evidence</h3>',
    unknowns.length?'<ul>'+unknowns.map(x=>'<li>'+esc(x)+'</li>').join("")+'</ul>':'<p>No unresolved evidence has been recorded. Confirm this is intentional before approval.</p>',
    '<h3>Board and executive scrutiny questions</h3><ol>'+questions.map(x=>'<li>'+esc(x)+'</li>').join("")+'</ol>',
    '<h3>Evidence ledger</h3>'+sourceHtml(sources),
    '<div class="notice">Pack completion: '+populated+'/'+COUNT_IDS.length+' fields populated. This is not a quality or readiness score. Separate verified facts from assumptions and obtain applicable legal, technical, financial or regulatory review before consequential use.</div>'
  ].join("");
  $("#dr-pack").hidden=false;
  $("#dr-pack").innerHTML=html;
  $("#dr-output-status").textContent="Pack built";
  $("#dr-output-status").className="status live";
  save();
}
function enc(o){
  const bytes=new TextEncoder().encode(JSON.stringify(o));
  let raw="";bytes.forEach(b=>raw+=String.fromCharCode(b));
  return btoa(raw).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");
}
function dec(s){
  try{
    const base=s.replace(/-/g,"+").replace(/_/g,"/")+"===".slice((s.length+3)%4);
    const raw=atob(base),bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  }catch(_){return null}
}
async function share(){
  const url=location.origin+location.pathname+"#review="+enc(state());
  if(url.length>12000){
    $("#dr-output-status").textContent="Pack too large for review URL";
    $("#dr-output-status").className="status next";
    build();
    $("#dr-pack").insertAdjacentHTML("beforeend",'<p class="notice">This pack is too large for a practical review URL. Use Print / Save PDF instead.</p>');
    return;
  }
  try{
    await navigator.clipboard.writeText(url);
    build();
    $("#dr-pack").insertAdjacentHTML("beforeend",'<p class="notice">Shareable review URL copied. The URL fragment contains the pack data; share only with intended recipients and do not use it for confidential material.</p>');
  }catch(_){
    $("#dr-output-status").textContent="Clipboard unavailable";
    $("#dr-output-status").className="status next";
  }
}
function clearWorkspace(){
  FIELD_IDS.forEach(id=>{
    const el=$("#dr-"+id);
    if(!el)return;
    if(el.tagName==="SELECT"){
      if(id==="status")el.value="Explore";
      else if(id==="evidence-state")el.value="Exploratory";
    }else el.value="";
  });
  importedSources=[];
  try{localStorage.removeItem(STORAGE_KEY);sessionStorage.removeItem("rrDecisionRoomImport")}catch(_){}
  renderLedger();updateCompletion();
  $("#dr-pack").hidden=true;
  $("#dr-pack").replaceChildren();
  $("#dr-output-status").textContent="Workspace cleared";
  $("#dr-output-status").className="status explore";
}
function loadReview(){
  if(!location.hash.startsWith("#review="))return false;
  const s=dec(location.hash.slice(8));
  if(!s)return false;
  FIELD_IDS.forEach(id=>setValue(id,s[id]||""));
  importedSources=safeSources(s.sources);
  renderLedger();updateCompletion();build(s);
  $("#dr-output-status").textContent="Review link loaded";
  return true;
}

$("#dr-build").onclick=()=>build();
$("#dr-print").onclick=()=>{build();window.print()};
$("#dr-import").onclick=importScenario;
$("#dr-import-context").onclick=importContext;
$("#dr-share").onclick=share;
$("#dr-clear").onclick=clearWorkspace;
FIELD_IDS.forEach(id=>$("#dr-"+id)?.addEventListener("input",save));
FIELD_IDS.forEach(id=>$("#dr-"+id)?.addEventListener("change",save));

if(!loadReview()){
  loadSaved();
  const params=new URLSearchParams(location.search);
  if(params.get("from")==="research"||params.get("from")==="briefing"||params.get("from")==="observatory")importContext();
}
renderLedger();
updateCompletion();
})();