(()=>{
"use strict";
const q=s=>document.querySelector(s), esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let data=[],filter="All";
function render(){
 const term=(q("#resource-q")?.value||"").trim().toLowerCase();
 const rows=data.filter(x=>(filter==="All"||x.type===filter)&&(!term||(x.title+" "+x.description+" "+x.category+" "+x.type).toLowerCase().includes(term)));
 q("#resource-count").textContent=rows.length+" resources shown";
 q("#resource-results").innerHTML=rows.map(x=>'<a class="card resource-card" href="'+esc(x.url)+'"><div class="resource-type">'+esc(x.type)+' · '+esc(x.category)+'</div><h3>'+esc(x.title)+'</h3><p>'+esc(x.description)+'</p><span class="go">Open resource →</span></a>').join("")||'<div class="panel"><p>No resources matched. Try a broader search.</p></div>';
}
fetch("/assets/resource-index.json",{cache:"force-cache"}).then(r=>r.json()).then(x=>{data=x.resources||[];render()}).catch(()=>{q("#resource-results").innerHTML='<div class="panel"><p>Resource index is temporarily unavailable.</p></div>'});
q("#resource-q")?.addEventListener("input",render);
document.querySelectorAll("[data-filter]").forEach(b=>b.addEventListener("click",()=>{filter=b.dataset.filter;document.querySelectorAll("[data-filter]").forEach(x=>x.classList.remove("is-active"));b.classList.add("is-active");render()}));
})();