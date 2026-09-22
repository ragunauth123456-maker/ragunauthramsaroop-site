(()=>{
"use strict";
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const n=v=>Math.max(0,Number.isFinite(Number(v))?Number(v):0);
const f=(v,p=1)=>Number(v).toLocaleString(undefined,{maximumFractionDigits:p});
function result(title,body){
  $("#out").innerHTML='<section class="result" id="tool-result"><h3>'+esc(title)+'</h3>'+body+'<div class="actions"><button class="btn alt" id="copy">Copy results</button><button class="btn alt" id="print">Print / Save PDF</button><button class="btn alt" id="share">Share this free tool</button></div></section>';
  $("#copy").onclick=async()=>{await navigator.clipboard.writeText($("#tool-result").innerText);$("#copy").textContent="Copied";};
  $("#print").onclick=()=>window.print();
  $("#share").onclick=async()=>{if(navigator.share)await navigator.share({title:document.title,url:location.href});else{await navigator.clipboard.writeText(location.href);$("#share").textContent="Link copied";}};
}
const field=(label,name,value,step="1",hint="")=>'<div class="field"><label>'+esc(label)+'</label><input name="'+name+'" type="number" min="0" step="'+step+'" value="'+value+'" required>'+(hint?'<small>'+esc(hint)+'</small>':"")+'</div>';
const metric=(value,label)=>'<div class="metric"><strong>'+esc(value)+'</strong><span>'+esc(label)+'</span></div>';
const root=$("#tool-ui"),type=document.body.dataset.tool;if(!root)return;
if(type==="water-demand-calculator"){
  root.innerHTML='<form class="panel" id="calc"><h2>Enter your water-demand scenario</h2><p>Every input is editable. Calculations run locally in your browser.</p><div class="tool-form">'+
    field("People served","people",100)+field("Litres per person each day","perPerson",100)+
    field("Additional site / process use (m³ per day)","process",4,"0.1")+
    field("Distribution and operational losses (%)","loss",10,"0.1")+
    field("Desired storage buffer (days)","buffer",7)+field("High-demand stress scenario (%)","surge",30,"0.1")+
    '</div><div class="actions"><button class="btn">Calculate water demand</button><button type="reset" class="btn alt">Reset</button></div></form><div id="out" aria-live="polite"></div>';
  $("#calc").onsubmit=e=>{
    e.preventDefault();const d=new FormData(e.target);
    const people=n(d.get("people")),per=n(d.get("perPerson")),process=n(d.get("process")),loss=n(d.get("loss")),buffer=n(d.get("buffer")),surge=n(d.get("surge"));
    if(loss>=100 || surge>1000 || buffer>3650){$("#out").innerHTML='<p class="notice">Check the loss, surge and storage-day assumptions.</p>';return;}
    const dailyNet=people*per/1000+process,withdrawal=dailyNet/(1-loss/100),stress=withdrawal*(1+surge/100),storage=withdrawal*buffer,stressStorage=stress*buffer;
    const body='<div class="metric-grid">'+metric(f(dailyNet)+" m³","Daily end-use demand")+metric(f(withdrawal)+" m³","Daily supply including losses")+metric(f(withdrawal*365,0)+" m³","Annual supply scenario")+metric(f(storage)+" m³","Usable storage for baseline buffer")+metric(f(stress)+" m³/day","Stress-scenario daily supply")+metric(f(stressStorage)+" m³","Storage under stress scenario")+'</div><h3>Planning notes</h3><p>The model assumes constant daily demand and losses. It excludes seasonal rainfall, source reliability, water quality, emergency reserves and fire-safety provisions. Do not use the output as a final engineering design.</p>';
    result("Water demand and storage scenario",body);
  };
}else if(type==="local-content-calculator"){
  root.innerHTML='<form class="panel" id="calc"><h2>Enter direct local-content figures</h2><p>Use your applicable definition of a qualifying local supplier and worker. Do not include unsupported economic multipliers.</p><div class="tool-form">'+
    field("Total procurement spend","totalSpend",5000000,"0.01")+
    field("Verified qualifying local procurement","localSpend",2000000,"0.01")+
    field("Local procurement target (%)","target",50,"0.1")+
    field("Number of qualifying local suppliers","suppliers",20)+
    field("Total workforce","workers",500)+field("Qualifying local workers","localWorkers",350)+
    '</div><div class="actions"><button class="btn">Calculate local content</button><button type="reset" class="btn alt">Reset</button></div></form><div id="out" aria-live="polite"></div>';
  $("#calc").onsubmit=e=>{
    e.preventDefault();const d=new FormData(e.target);const total=n(d.get("totalSpend")),local=n(d.get("localSpend")),target=n(d.get("target")),suppliers=n(d.get("suppliers")),workers=n(d.get("workers")),localWorkers=n(d.get("localWorkers"));
    if(local>total||localWorkers>workers||target>100){$("#out").innerHTML='<p class="notice">Local procurement cannot exceed total procurement, local workers cannot exceed total workforce and the target must be 0–100%.</p>';return;}
    const share=total?100*local/total:0,workShare=workers?100*localWorkers/workers:0,required=total*target/100,shortfall=Math.max(0,required-local);
    const body='<div class="metric-grid">'+metric(f(share)+"%","Qualifying local procurement share")+metric(f(workShare)+"%","Qualifying local workforce share")+metric(f(local,0),"Verified local procurement (entered currency)")+metric(f(required,0),"Procurement implied by target")+metric(f(shortfall,0),"Additional local spend for target")+metric(f(suppliers,0),"Entered local suppliers")+'</div><h3>Interpretation</h3><p>A target is a scenario, not a legal requirement unless confirmed independently. Verify supplier classification, spend recognition and workforce eligibility against current applicable rules. No indirect job or economic multiplier is assumed.</p>';
    result("Direct local-content scenario",body);
  };
}
})();