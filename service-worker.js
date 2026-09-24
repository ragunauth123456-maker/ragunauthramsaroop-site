const V="rr-public-v5";
const CORE=[
"/","/start/","/tools/","/resources/","/search/","/smart/","/my-toolkit/","/tool-finder/","/methodology/","/embed/","/scenario-lab/",
"/assets/platform.css","/assets/platform.js","/assets/accessibility.js","/assets/i18n.js","/assets/search-index.json","/assets/semantic-index.json",
"/assets/smart-search.js","/assets/site-brain.js","/assets/brain-worker.js","/assets/smart-guide.js",
"/assets/vendor/minisearch-7.2.0.js","/assets/vendor/comlink-4.4.2.js","/assets/vendor/idb-keyval-6.3.0.js",
"/pagefind/pagefind.js","/tools/assets/tools.css","/tools/assets/tool-pro.js","/tools/assets/tool-enhancements.js","/tools/assets/report-export.js","/tools/assets/engagement-tracking.js",
"/data/tool-method-details.json","/api/v1/catalog.json","/favicon-96.png",
"/tools/esg-readiness/","/tools/mining-carbon-calculator/","/tools/renewable-transition-calculator/","/tools/stakeholder-mapper/",
"/tools/government-relations-risk/","/tools/social-licence-health/","/tools/executive-brief-generator/","/tools/board-question-generator/",
"/tools/career-evidence-builder/","/tools/job-fit-analyzer/","/tools/speaking-question-generator/","/tools/white-paper-navigator/",
"/tools/guyana-investment-dashboard/","/tools/guyana-regulatory-navigator/","/tools/responsible-mining-assessment/","/tools/executive-templates/",
"/tools/water-demand-calculator/","/tools/local-content-calculator/","/tools/diesel-cost-carbon/","/tools/solar-battery-sizing/",
"/tools/community-investment-prioritizer/","/tools/esg-materiality-matrix/","/tools/grievance-trend-analyzer/","/tools/executive-100-day-plan/",
"/tools/government-meeting-brief/","/tools/responsible-procurement-assessment/"
];
self.addEventListener("install",e=>e.waitUntil(caches.open(V).then(c=>Promise.all(CORE.map(u=>c.add(u).catch(()=>null)))).then(()=>self.skipWaiting())));
self.addEventListener("activate",e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
async function nav(req){const c=await caches.open(V);try{const timeout=new Promise((_,rej)=>setTimeout(()=>rej(new Error("timeout")),4000));const r=await Promise.race([fetch(req),timeout]);if(r&&r.ok)c.put(req,r.clone());return r}catch{return await c.match(req)||await c.match("/tools/")||await c.match("/start/")}}
async function asset(req){const c=await caches.open(V),hit=await c.match(req);if(hit){fetch(req).then(r=>{if(r.ok)c.put(req,r.clone())}).catch(()=>{});return hit}const r=await fetch(req);if(r.ok)c.put(req,r.clone());return r}
self.addEventListener("fetch",e=>{if(e.request.method!=="GET")return;const u=new URL(e.request.url);if(u.origin!==location.origin)return;if(e.request.mode==="navigate")e.respondWith(nav(e.request));else if(/\.(?:js|css|json|png|webp|svg|ico|wasm)$/.test(u.pathname))e.respondWith(asset(e.request));else e.respondWith(nav(e.request))});
self.addEventListener("message",e=>{if(e.data?.type!=="RR_PREFETCH"||!Array.isArray(e.data.urls))return;const urls=e.data.urls.filter(u=>typeof u==="string"&&u.startsWith("/")).slice(0,4);e.waitUntil(caches.open(V).then(c=>Promise.all(urls.map(u=>c.add(u).catch(()=>null)))))});
