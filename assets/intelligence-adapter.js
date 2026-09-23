(()=>{
"use strict";
const cfg={edge:(window.RR_EDGE_ENDPOINT||"").replace(/\/$/,"")};
async function local(kind,payload){
 if(kind==="search"){const r=await fetch("/assets/search-index.json",{cache:"force-cache"});const j=await r.json();return j.documents||[]}
 if(kind==="sources"){const r=await fetch("/data/source-monitor.json",{cache:"no-cache"});return r.ok?await r.json():{sources:[]}}
 if(kind==="guyana"){const r=await fetch("/data/guyana-live.json",{cache:"no-cache"});return r.ok?await r.json():{metrics:[]}}
 return {mode:"local",ok:true,payload};
}
window.RRIntelligence={async request(kind,payload={}){
 if(cfg.edge){try{const r=await fetch(cfg.edge+"/v1/"+encodeURIComponent(kind),{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(payload)});if(r.ok)return await r.json()}catch(e){}}
 return local(kind,payload);
},mode(){return cfg.edge?"edge-preferred":"local-first"}};
})();