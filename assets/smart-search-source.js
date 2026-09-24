import { create, insertMultiple, search } from "@orama/orama";

let semanticPayload=null, db=null, embedder=null, searchDocs=null;
const MODEL_CDN="https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.3.0/+esm";
const MODEL_ID="Xenova/all-MiniLM-L6-v2";

function decodeVector(item,dimensions=384){
  const raw=atob(item.q), bytes=new Int8Array(dimensions);
  for(let i=0;i<dimensions;i++){const n=raw.charCodeAt(i);bytes[i]=n>127?n-256:n}
  const out=new Array(dimensions),s=Number(item.scale)||1;
  for(let i=0;i<dimensions;i++)out[i]=bytes[i]*s;
  return out;
}
async function loadPayload(){
  if(semanticPayload)return semanticPayload;
  const r=await fetch("/assets/semantic-index.json",{cache:"force-cache"});
  if(!r.ok)throw new Error("Semantic index unavailable");
  semanticPayload=await r.json();
  return semanticPayload;
}
async function loadSearchDocs(){
  if(searchDocs)return searchDocs;
  const r=await fetch("/assets/search-index.json",{cache:"force-cache"});
  const j=await r.json();searchDocs=j.documents||[];return searchDocs;
}
async function initDb(){
  if(db)return db;
  const p=await loadPayload();
  db=await create({schema:{url:"string",title:"string",description:"string",type:"string",embedding:"vector[384]"}});
  await insertMultiple(db,p.documents.map(x=>({url:x.url,title:x.title,description:x.description||"",type:x.type||"Public",embedding:decodeVector(x,p.dimensions)})));
  return db;
}
async function loadEmbedder(onProgress){
  if(embedder)return embedder;
  onProgress?.({status:"loading",message:"Loading the private semantic model on this device…"});
  const mod=await import(MODEL_CDN);
  if(mod.env){mod.env.allowRemoteModels=true;mod.env.useBrowserCache=true}
  embedder=await mod.pipeline("feature-extraction",MODEL_ID,{dtype:"q8",progress_callback:p=>onProgress?.(p)});
  onProgress?.({status:"ready",message:"Semantic model ready on this device."});
  return embedder;
}
async function vectorForQuery(query,onProgress){
  const pipe=await loadEmbedder(onProgress);
  const out=await pipe(query,{pooling:"mean",normalize:true});
  return Array.from(out.data);
}
async function semanticSearch(query,{limit=12,type=null,onProgress=null}={}){
  const database=await initDb(),vector=await vectorForQuery(query,onProgress);
  const opts={mode:"hybrid",term:query,vector:{property:"embedding",value:vector},similarity:0.12,limit};
  if(type&&type!=="All")opts.where={type:{eq:type}};
  const res=await search(database,opts);
  return (res.hits||[]).map(h=>({...h.document,score:h.score}));
}
async function recommendByUrl(url,limit=4){
  return recommendAdaptive(url,[],limit);
}
async function recommendAdaptive(currentUrl,historyUrls=[],limit=4){
  const p=await loadPayload(),all=[currentUrl,...historyUrls.filter(x=>x&&x!==currentUrl).slice(0,5)],weighted=[];
  let totalWeight=0;
  all.forEach((url,i)=>{const item=p.documents.find(x=>x.url===url);if(!item)return;const w=i===0?1:Math.max(.15,.5/(i+1));weighted.push({v:decodeVector(item,p.dimensions),w,url});totalWeight+=w});
  if(!weighted.length)return [];
  const vector=new Array(p.dimensions).fill(0);
  for(const x of weighted)for(let i=0;i<vector.length;i++)vector[i]+=x.v[i]*x.w;
  let norm=Math.sqrt(vector.reduce((n,v)=>n+v*v,0))||1;for(let i=0;i<vector.length;i++)vector[i]/=norm;
  const database=await initDb(),res=await search(database,{mode:"vector",vector:{property:"embedding",value:vector},similarity:0.30,limit:limit+8});
  const exclude=new Set(all);
  return (res.hits||[]).map(h=>({...h.document,score:h.score})).filter(x=>!exclude.has(x.url)).slice(0,limit);
}
function splitSentences(text){return String(text||"").split(/(?<=[.!?])\s+/).map(x=>x.trim()).filter(x=>x.length>45&&x.length<520)}
function norm(s){return String(s||"").toLowerCase().normalize("NFKD").replace(/[^\w\s-]/g," ").replace(/\s+/g," ").trim()}
function terms(s){return [...new Set(norm(s).split(" ").filter(x=>x.length>2&&!["the","and","for","with","from","what","how","who","why","when","where","this","that","are","was","were","can","should","would","about"].includes(x)))]}
async function answer(query,{limit=5,onProgress=null}={}){
  const hits=await semanticSearch(query,{limit,onProgress}),docs=await loadSearchDocs(),ts=terms(query),parts=[];
  for(let i=0;i<hits.length;i++){
    const full=docs.find(d=>d.url===hits[i].url),pool=splitSentences(full?.text||full?.description||hits[i].description);
    const ranked=pool.map(s=>({s,score:ts.reduce((n,t)=>n+(norm(s).includes(t)?1:0),0)})).sort((a,b)=>b.score-a.score);
    const best=(ranked.find(x=>x.score>0)||ranked[0])?.s||hits[i].description;
    if(best)parts.push({n:i+1,text:best,url:hits[i].url,title:hits[i].title,type:hits[i].type});
  }
  return {answer:parts.slice(0,4).map(x=>"["+x.n+"] "+x.text).join(" "),sources:parts};
}
function intent(query){
 const q=norm(query),map=[
  ["mining",["mine","mining","gold","diesel","carbon","ore","mineral"]],
  ["energy",["energy","solar","battery","power","renewable","electricity"]],
  ["water",["water","storage","freshwater"]],
  ["government",["government","regulatory","regulator","permit","agency","minister"]],
  ["esg",["esg","sustainability","materiality","governance","climate"]],
  ["community",["community","grievance","stakeholder","social","local content"]],
  ["executive",["board","executive","leadership","decision","100 day"]],
  ["career",["career","job","resume","cv","interview","recruiter"]]
 ];let best={name:"general",score:0};for(const [name,words] of map){const score=words.reduce((n,w)=>n+(q.includes(w)?1:0),0);if(score>best.score)best={name,score}}return best.name
}
window.RRSmartSearch={semanticSearch,recommendByUrl,recommendAdaptive,answer,intent,model:MODEL_ID};
export { semanticSearch,recommendByUrl,recommendAdaptive,answer,intent };
