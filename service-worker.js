/* Network-first pages, on-demand assets and a compact offline shell. */
const V="rr-public-v10";
const CORE=["/","/start/","/assets/home.css","/assets/site.css","/assets/platform.css","/tools/assets/tools.css","/favicon-96.png"];
const MAX_DYNAMIC_ENTRIES=100;

self.addEventListener("install",event=>{
  event.waitUntil(caches.open(V)
    .then(cache=>Promise.allSettled(CORE.map(url=>cache.add(url))))
    .then(()=>self.skipWaiting()));
});

self.addEventListener("activate",event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(
    keys.filter(k=>k.startsWith("rr-public-v")&&k!==V).map(k=>caches.delete(k))
  )).then(()=>self.clients.claim()));
});

async function remember(cache,request,response){
  if(!response||!response.ok)return;
  try{
    await cache.put(request,response.clone());
    const keys=await cache.keys();
    if(keys.length>MAX_DYNAMIC_ENTRIES){
      for(const key of keys.slice(0,keys.length-MAX_DYNAMIC_ENTRIES)){
        if(!CORE.includes(new URL(key.url).pathname))await cache.delete(key);
      }
    }
  }catch{}
}

async function navigation(request,event){
  const cache=await caches.open(V);
  // Prefer the network for fresh content after every deployment.
  try{
    const response=await fetch(request);
    if(response.ok)event.waitUntil(remember(cache,request,response.clone()));
    return response;
  }catch{
    // Never substitute /start/ or / for a different URL. This previously
    // displayed the Start page at /tools/geolibre/ when connectivity failed.
    const exact=await cache.match(request,{ignoreSearch:true});
    if(exact)return exact;
    return new Response(
      '<!doctype html><html lang="en"><meta charset="utf-8">'+
      '<meta name="viewport" content="width=device-width,initial-scale=1">'+
      '<title>Connection unavailable | Ragunauth Ramsaroop</title>'+
      '<style>body{margin:0;background:#f4f8f6;color:#17382d;font:17px/1.6 system-ui,sans-serif;display:grid;min-height:100vh;place-items:center}main{max-width:570px;margin:22px;padding:32px;border-radius:18px;background:white;box-shadow:0 12px 36px #17382d18}h1{margin-top:0;font-size:29px}a,button{display:inline-block;margin:8px 12px 0 0;padding:11px 18px;border:0;border-radius:9px;background:#12382c;color:white;font:700 15px system-ui;text-decoration:none;cursor:pointer}</style>'+
      '<main><h1>Connection unavailable</h1>'+
      '<p>This page has not loaded. Check your connection and retry. No other page has been substituted.</p>'+
      '<button onclick="location.reload()">Try again</button>'+
      '<a href="/">Home</a></main></html>',
      {status:503,statusText:"Offline",headers:{"Content-Type":"text/html; charset=utf-8","Cache-Control":"no-store"}}
    );
  }
}

function validStaticResponse(response,pathname){
  if(!response||!response.ok)return false;
  const type=(response.headers.get("content-type")||"").toLowerCase();
  if(pathname.endsWith(".css"))return type.includes("text/css");
  if(pathname.endsWith(".js"))return type.includes("javascript");
  return true;
}

async function asset(request,immutable,event){
  const cache=await caches.open(V);
  const pathname=new URL(request.url).pathname;
  if(immutable){
    const hit=await cache.match(request);
    if(hit&&validStaticResponse(hit,pathname))return hit;
    if(hit)await cache.delete(request);
  }
  try{
    const response=await fetch(request);
    if(validStaticResponse(response,pathname))event.waitUntil(remember(cache,request,response.clone()));
    return response;
  }catch{
    const hit=await cache.match(request);
    return hit&&validStaticResponse(hit,pathname)?hit:Response.error();
  }
}

self.addEventListener("fetch",event=>{
  const request=event.request;
  if(request.method!=="GET")return;
  const url=new URL(request.url);
  if(url.origin!==self.location.origin)return;
  if(request.mode==="navigate"){
    event.respondWith(navigation(request,event));
  }else if(/\.(?:js|css|json|png|jpg|jpeg|webp|avif|svg|ico|woff2|wasm)$/.test(url.pathname)){
    event.respondWith(asset(request,url.pathname.startsWith("/_next/static/"),event));
  }
});

self.addEventListener("message",event=>{
  if(event.data?.type!=="RR_PREFETCH"||!Array.isArray(event.data.urls))return;
  const urls=event.data.urls.filter(url=>typeof url==="string"&&url.startsWith("/")&&!url.startsWith("//")).slice(0,4);
  event.waitUntil(caches.open(V).then(cache=>Promise.allSettled(
    urls.map(url=>cache.add(url))
  )));
});
