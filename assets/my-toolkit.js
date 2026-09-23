(()=>{
"use strict";
const q=s=>document.querySelector(s),esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const j=(k,d=[])=>{try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch{return d}};
const resources=()=>j("rrToolkitV1"),recent=()=>j("rrRecentToolsV1"),reports=()=>j("rrReportHistoryV1");
function scenarios(){const out=[];for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(!k?.startsWith("rrScenarios:"))continue;const slug=k.slice(12),arr=j(k);arr.forEach((x,idx)=>out.push({...x,slug,index:idx}))}return out.sort((a,b)=>(b.savedAt||0)-(a.savedAt||0))}
function card(title,meta,body,actions=""){return '<article class="card toolkit-card"><div class="resource-type">'+esc(meta)+'</div><h3>'+esc(title)+'</h3><p>'+body+'</p>'+actions+'</article>'}
function render(){
 const res=resources(),rec=recent(),sc=scenarios(),rep=reports();
 q("#toolkit-summary").innerHTML='<div class="metric-grid"><div class="metric"><strong>'+res.length+'</strong><span>saved resources</span></div><div class="metric"><strong>'+sc.length+'</strong><span>saved scenarios</span></div><div class="metric"><strong>'+rec.length+'</strong><span>recent tools</span></div><div class="metric"><strong>'+rep.length+'</strong><span>report exports recorded</span></div></div>';
 q("#toolkit-resources").innerHTML=res.map((x,i)=>card(x.title||"Saved resource","Saved resource",'<a href="'+esc(x.url)+'">'+esc(x.desc||x.url||"Open saved resource")+'</a>','<button class="btn alt" data-remove-resource="'+i+'">Remove</button>')).join("")||'<p class="muted">No saved resources yet. Use Save on public pages.</p>';
 q("#toolkit-recent").innerHTML=rec.slice(0,12).map(x=>card(x.title||x.slug,"Recent tool",'<a href="'+esc(x.url)+'">Open tool →</a><br><span class="muted">'+new Date(x.at).toLocaleString()+'</span>')).join("")||'<p class="muted">No recent tool history on this device yet.</p>';
 q("#toolkit-scenarios").innerHTML=sc.slice(0,20).map(x=>card(x.name||"Saved scenario",x.slug,'Saved '+new Date(x.savedAt).toLocaleString()+'<br><a href="/tools/'+esc(x.slug)+'/">Open related tool →</a>','<button class="btn alt" data-delete-scenario="'+esc(x.slug)+'" data-index="'+x.index+'">Delete</button>')).join("")||'<p class="muted">No saved tool scenarios yet.</p>';
 q("#toolkit-reports").innerHTML=rep.slice(0,20).map(x=>card(x.title||x.slug,"Report history",esc(x.type||"report")+' · '+new Date(x.at).toLocaleString()+'<br><a href="'+esc(x.url||("/tools/"+x.slug+"/"))+'">Return to tool →</a>')).join("")||'<p class="muted">No report exports recorded yet.</p>';
 document.querySelectorAll("[data-remove-resource]").forEach(b=>b.onclick=()=>{const a=resources();a.splice(Number(b.dataset.removeResource),1);localStorage.setItem("rrToolkitV1",JSON.stringify(a));render()});
 document.querySelectorAll("[data-delete-scenario]").forEach(b=>b.onclick=()=>{const k="rrScenarios:"+b.dataset.deleteScenario,a=j(k);a.splice(Number(b.dataset.index),1);localStorage.setItem(k,JSON.stringify(a));render()});
}
function exportWorkspace(){const payload={exported:new Date().toISOString(),resources:resources(),recentTools:recent(),scenarios:scenarios().map(({index,...x})=>x),reports:reports()};const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"}),u=URL.createObjectURL(blob),a=document.createElement("a");a.href=u;a.download="rr-my-toolkit-workspace.json";a.click();URL.revokeObjectURL(u);window.rrTrack?.("toolkit_exported")}
q("#toolkit-export")?.addEventListener("click",exportWorkspace);
q("#toolkit-clear")?.addEventListener("click",()=>{if(!confirm("Clear saved resources, scenarios, recent tool history and report history from this browser?"))return;["rrToolkitV1","rrRecentToolsV1","rrReportHistoryV1"].forEach(k=>localStorage.removeItem(k));[...Array(localStorage.length)].forEach(()=>{});const ks=[];for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k?.startsWith("rrScenarios:"))ks.push(k)}ks.forEach(k=>localStorage.removeItem(k));render();window.rrTrack?.("toolkit_cleared")});
render();
})();