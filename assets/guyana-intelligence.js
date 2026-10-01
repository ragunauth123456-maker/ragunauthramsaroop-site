(()=>{
"use strict";

const state={data:null,resources:[],filter:"All",sector:"mining"};
const $=selector=>document.querySelector(selector);
const $$=selector=>Array.from(document.querySelectorAll(selector));
const esc=value=>String(value==null?"":value).replace(/[&<>"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const external=href=>/^https?:\/\//i.test(String(href||""));

function linkMarkup(item,withRole){
  const attrs=external(item.href)?' target="_blank" rel="noopener noreferrer"':"";
  return '<a href="'+esc(item.href)+'"'+attrs+'><strong>'+esc(item.label)+'</strong>'+(withRole&&item.role?'<small>'+esc(item.role)+'</small>':'')+'</a>';
}

function resourceClass(item){
  const text=(String(item.title||"")+" "+String(item.description||"")+" "+String(item.category||"")).toLowerCase();
  if(/mining|gold|mineral|mine/.test(text)) return "Mining";
  if(/energy|power|solar|renewable|electric|diesel/.test(text)) return "Energy";
  if(/regulat|government|institution|permit|standard|aviation/.test(text)) return "Regulation";
  return "Economy";
}

function isGuyanaResource(item){
  const text=(String(item.title||"")+" "+String(item.description||"")+" "+String(item.category||"")).toLowerCase();
  return /guyana|local content|power demand|development bank|lcds|carbon credits|biodiversity alliance|omai|karpowership/.test(text);
}

function renderSectorButtons(){
  const box=$("#sector-buttons");
  if(!box||!state.data) return;
  box.innerHTML=state.data.sectors.map(sector=>
    '<button type="button" role="listitem" data-sector="'+esc(sector.id)+'" class="'+(sector.id===state.sector?"is-active":"")+'">'+esc(sector.label)+'</button>'
  ).join("");
  $$("[data-sector]").forEach(button=>{
    button.addEventListener("click",()=>{
      state.sector=button.dataset.sector;
      renderSectorButtons();
      renderSector();
    });
  });
}

function renderSector(){
  if(!state.data) return;
  const sector=state.data.sectors.find(item=>item.id===state.sector)||state.data.sectors[0];
  if(!sector) return;
  $("#sector-name").textContent=sector.label;
  $("#sector-summary").textContent=sector.summary;
  $("#sector-kicker").textContent="Sector pathway · "+sector.label;
  $("#sector-questions").innerHTML=sector.questions.map(question=>"<li>"+esc(question)+"</li>").join("");
  $("#sector-sources").innerHTML=sector.sources.map(item=>linkMarkup(item,true)).join("");
  $("#sector-research").innerHTML=sector.research.map(item=>linkMarkup(item,false)).join("");
  $("#sector-tools").innerHTML=sector.tools.map(item=>linkMarkup(item,false)).join("");
  const ask=$("#sector-ask");
  if(ask){
    ask.onclick=()=>{
      storeGuyanaQuestion("What should decision-makers examine in Guyana's "+sector.label+" sector, based on the published research and public-source evidence?");
    };
  }
}

function renderQuickLinks(){
  const box=$("#quick-links");
  if(!box||!state.data) return;
  box.innerHTML=state.data.quickLinks.map(item=>
    '<a href="'+esc(item.href)+'"><span>Guyana intelligence</span><h3>'+esc(item.label)+'</h3><p>'+esc(item.description)+'</p></a>'
  ).join("");
}

function renderResources(){
  const box=$("#gy-results");
  if(!box) return;
  const term=String($("#gy-q")?.value||"").trim().toLowerCase();
  const rows=state.resources
    .filter(isGuyanaResource)
    .filter(item=>state.filter==="All"||resourceClass(item)===state.filter)
    .filter(item=>!term||(String(item.title||"")+" "+String(item.description||"")+" "+String(item.category||"")).toLowerCase().includes(term))
    .slice(0,24);

  box.innerHTML=rows.length?rows.map(item=>
    '<a class="resource-card" href="'+esc(item.url)+'"><div class="resource-type">'+esc(resourceClass(item))+' · '+esc(item.type||"Resource")+'</div><h3>'+esc(item.title)+'</h3><p>'+esc(item.description)+'</p><span class="go">Open resource →</span></a>'
  ).join(""):'<article class="resource-card"><div class="resource-type">No match</div><h3>Try a broader Guyana topic.</h3><p>Search energy, mining, regulation, local content, water, climate or development.</p></article>';
}

function storeGuyanaQuestion(question){
  const text=String(question||"").trim().slice(0,700);
  if(text.length<4) return;
  try{
    sessionStorage.setItem("rrGuyanaQuestion",JSON.stringify({question:text,createdAt:Date.now()}));
  }catch(_){}
  location.href="/ask-research/?from=guyana";
}

async function init(){
  try{
    const response=await fetch("/assets/guyana-intelligence-data.json",{cache:"force-cache"});
    if(!response.ok) throw new Error("data_unavailable");
    state.data=await response.json();
    renderSectorButtons();
    renderSector();
    renderQuickLinks();
  }catch(_){
    const summary=$("#sector-summary");
    if(summary) summary.textContent="The structured sector index is unavailable. Use the direct tools and research links below.";
  }

  try{
    const response=await fetch("/assets/resource-index.json",{cache:"force-cache"});
    if(response.ok){
      const payload=await response.json();
      state.resources=Array.isArray(payload.resources)?payload.resources:[];
    }
  }catch(_){}
  renderResources();

  $("#gy-q")?.addEventListener("input",renderResources);
  $$("[data-gy-filter]").forEach(button=>{
    button.addEventListener("click",()=>{
      state.filter=button.dataset.gyFilter||"All";
      $$("[data-gy-filter]").forEach(item=>item.classList.remove("is-active"));
      button.classList.add("is-active");
      renderResources();
    });
  });

  $("#guyana-ask-form")?.addEventListener("submit",event=>{
    event.preventDefault();
    storeGuyanaQuestion($("#guyana-question")?.value);
  });
}

init();
})();