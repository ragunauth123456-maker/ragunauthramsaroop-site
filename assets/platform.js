(()=>{
"use strict";
if(new URL(location.href).searchParams.get("embed")==="1"){document.documentElement.classList.add("rr-embed-mode")}
const KEY="rrToolkitV1", esc=s=>String(s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
if("serviceWorker" in navigator) addEventListener("load",()=>navigator.serviceWorker.register("/service-worker.js").catch(()=>{}));
document.addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k"){e.preventDefault();location.href="/search/"}});
function saved(){try{return JSON.parse(localStorage.getItem(KEY)||"[]")}catch{return []}}
function savePage(){
 let a=saved(), url=location.pathname, title=(document.querySelector("h1")?.textContent||document.title).trim(), desc=document.querySelector('meta[name="description"]')?.content||"";
 if(!a.some(x=>x.url===url)){a.unshift({url,title,desc,savedAt:new Date().toISOString()});localStorage.setItem(KEY,JSON.stringify(a.slice(0,80)));return true}
 return false;
}
if(!["/","/my-toolkit/","/search/"].includes(location.pathname)){
 const dock=document.createElement("div");dock.className="rr-utility-dock";dock.innerHTML='<a href="/search/" title="Search the site">Search</a><button type="button" id="rr-save-page">Save</button><a href="/my-toolkit/" title="Open saved items">Toolkit</a>';
 document.body.appendChild(dock); dock.querySelector("#rr-save-page").onclick=e=>{const ok=savePage();e.currentTarget.textContent=ok?"Saved":"Saved already";};
}
document.querySelectorAll(".rr-platform-nav").forEach(n=>{if(!n.querySelector('a[href="/search/"]'))n.insertAdjacentHTML("afterbegin",'<a href="/search/">Search</a><a href="/my-toolkit/">My Toolkit</a><a href="/tool-finder/">Tool Finder</a>')});
const professional=["/executive-profile/","/leadership/","/corporate-affairs/","/esg-social-impact/","/compliance-governance/","/authority/","/case-studies/"];
if(professional.includes(location.pathname)&&!document.querySelector(".rr-conversion-mini")){
 const main=document.querySelector("main .wrap")||document.querySelector("main");if(main){const s=document.createElement("section");s.className="panel rr-conversion-mini";s.innerHTML='<h2>Professional engagement</h2><p>Review the route relevant to executive search, board and advisory work, speaking, media or institutional projects.</p><div class="actions"><a class="btn" href="/professional-engagement/">Engagement routes</a><a class="btn alt" href="/engage/">Contact</a></div>';main.appendChild(s)}
}
async function related(){
 if(document.querySelector(".rr-related")||location.pathname==="/")return;
 try{const r=await fetch("/assets/search-index.json",{cache:"force-cache"}),j=await r.json(),title=(document.querySelector("h1")?.textContent||document.title).toLowerCase(),terms=title.split(/\W+/).filter(x=>x.length>4),rows=j.documents.filter(x=>x.url!==location.pathname).map(x=>({x,s:terms.reduce((n,t)=>n+(String(x.title+" "+x.description).toLowerCase().includes(t)?1:0),0)})).filter(z=>z.s>0).sort((a,b)=>b.s-a.s).slice(0,3);if(!rows.length)return;const main=document.querySelector("main .wrap")||document.querySelector("main");if(!main)return;const s=document.createElement("section");s.className="panel rr-related";s.innerHTML='<h2>Related resources</h2><div class="related-grid">'+rows.map(z=>'<a href="'+esc(z.x.url)+'"><strong>'+esc(z.x.title)+'</strong><span>'+esc(z.x.type)+'</span></a>').join("")+'</div>';main.appendChild(s)}catch{}
}
related();
window.RRSaveCurrentPage=savePage;
})();