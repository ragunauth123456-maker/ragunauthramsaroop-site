(()=>{
"use strict";
const cards=[...document.querySelectorAll("#tool-grid .card")], search=document.querySelector("#tool-search-input"), sort=document.querySelector("#tool-sort"), count=document.querySelector("#visible-tool-count"), empty=document.querySelector("#tool-filter-empty"), chips=[...document.querySelectorAll(".filter-chip")], grid=document.querySelector("#tool-grid");
if(!cards.length)return;
let filter="all";
const usageKey="rrToolUsageV1";const usage=JSON.parse(localStorage.getItem(usageKey)||"{}");
cards.forEach(c=>{const slug=c.dataset.slug;if(usage[slug]){const n=document.createElement("span");n.className="rr-personal-usage";n.textContent="Used by you "+usage[slug]+"×";c.querySelector(".tool-category")?.append(n)}c.addEventListener("click",()=>{usage[slug]=(usage[slug]||0)+1;localStorage.setItem(usageKey,JSON.stringify(usage))})});
function run(){const q=(search?.value||"").trim().toLowerCase();let shown=0;cards.forEach(c=>{const hay=(c.textContent+" "+c.dataset.group+" "+c.dataset.slug).toLowerCase();const ok=(filter==="all"||c.dataset.group===filter)&&(!q||hay.includes(q));c.hidden=!ok;if(ok)shown++});if(count)count.textContent=shown;if(empty)empty.hidden=shown>0;}
chips.forEach(b=>b.addEventListener("click",()=>{chips.forEach(x=>x.classList.remove("active"));b.classList.add("active");filter=b.dataset.filter;run()}));search?.addEventListener("input",run);
sort?.addEventListener("change",()=>{const list=cards.slice();if(sort.value==="az")list.sort((a,b)=>a.querySelector("h3").textContent.localeCompare(b.querySelector("h3").textContent));else if(sort.value==="category")list.sort((a,b)=>(a.dataset.group+a.querySelector("h3").textContent).localeCompare(b.dataset.group+b.querySelector("h3").textContent));else list.sort((a,b)=>Number(a.querySelector(".num").textContent)-Number(b.querySelector(".num").textContent));list.forEach(c=>grid.append(c));run()});
const params=new URLSearchParams(location.search),cat=params.get("category"),term=params.get("q");if(term&&search){search.value=term}if(cat){const b=chips.find(x=>x.dataset.filter===cat);if(b)b.click();else run()}else run();
})();