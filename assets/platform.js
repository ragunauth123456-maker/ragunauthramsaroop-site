(()=>{
"use strict";
const RR_SITE_CSS="/assets/site.css?v=20260928-2";
const RR_THEME_CSS="/assets/theme-uniform.css?v=20260929-1";
if(!document.querySelector('link[href^="/assets/theme-uniform.css"]')){
  const rrTheme=document.createElement("link");
  rrTheme.rel="stylesheet";
  rrTheme.href=RR_THEME_CSS;
  rrTheme.dataset.rrTheme="1";
  document.head.appendChild(rrTheme);
}

if(!document.querySelector('link[href^="/assets/site.css"]')){
  const rrStyle=document.createElement("link");
  rrStyle.rel="stylesheet";
  rrStyle.href=RR_SITE_CSS;
  rrStyle.dataset.rrFallback="1";
  document.head.appendChild(rrStyle);
}
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
 try{const r=await fetch("/assets/resource-index.json",{cache:"force-cache"}),j=await r.json(),title=(document.querySelector("h1")?.textContent||document.title).toLowerCase(),terms=title.split(/\W+/).filter(x=>x.length>4),rows=(j.resources||[]).filter(x=>x.url!==location.pathname).map(x=>({x,s:terms.reduce((n,t)=>n+(String(x.title+" "+x.description).toLowerCase().includes(t)?1:0),0)})).filter(z=>z.s>0).sort((a,b)=>b.s-a.s).slice(0,3);if(!rows.length)return;const main=document.querySelector("main .wrap")||document.querySelector("main");if(!main)return;const s=document.createElement("section");s.className="panel rr-related";s.innerHTML='<h2>Related resources</h2><div class="related-grid">'+rows.map(z=>'<a href="'+esc(z.x.url)+'"><strong>'+esc(z.x.title)+'</strong><span>'+esc(z.x.type)+'</span></a>').join("")+'</div>';main.appendChild(s)}catch{}
}
/* Related results need a large index. Delay work until after first paint. */
function afterLoadIdle(fn, delay) {
  const schedule=()=>{
    setTimeout(()=>{
      const run=()=>{
        if(document.visibilityState!=="visible"){
          const onVisible=()=>{
            if(document.visibilityState==="visible"){
              document.removeEventListener("visibilitychange",onVisible);
              fn();
            }
          };
          document.addEventListener("visibilitychange",onVisible);
        }else fn();
      };
      if("requestIdleCallback" in window) requestIdleCallback(run,{timeout:7000});
      else run();
    },delay);
  };
  if(document.readyState==="complete")schedule();
  else addEventListener("load",schedule,{once:true});
}
if(!["/","/smart/","/search/"].includes(location.pathname))afterLoadIdle(related,2200);
const startBrain=()=>import("/assets/site-brain.js").catch(()=>{});
if(["/smart/","/search/"].includes(location.pathname))startBrain();
else if(location.pathname!=="/")afterLoadIdle(startBrain,4500);
else afterLoadIdle(startBrain,12000);
window.RRSaveCurrentPage=savePage;
})();