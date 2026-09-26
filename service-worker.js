/* Network-first pages, on-demand assets and a four-resource offline shell. */
const V="rr-public-v6";
const CORE=["/","/start/","/assets/platform.css","/favicon-96.png"];
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
    return await cache.match(request)||await cache.match("/start/")||Response.error();
  }
}

async function asset(request,immutable,event){
  const cache=await caches.open(V);
  if(immutable){
    const hit=await cache.match(request);
    if(hit)return hit;
  }
  try{
    const response=await fetch(request);
    if(response.ok)event.waitUntil(remember(cache,request,response.clone()));
    return response;
  }catch{
    return await cache.match(request)||Response.error();
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
