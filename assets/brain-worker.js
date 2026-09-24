importScripts('/assets/vendor/minisearch-7.2.0.js','/assets/vendor/comlink-4.4.2.js');
let ready=false,index=null,docs=[],byId=new Map();
const STOP=new Set('the a an and or of to in for on with from by is are be this that your you our as at into about'.split(' '));
const INTENTS={
  mining:['mining','mine','gold','diesel','carbon','emissions','responsible mining','critical minerals'],
  energy:['energy','solar','battery','renewable','power','electricity','diesel','transition'],
  water:['water','storage','demand','freshwater','resilience'],
  government:['government','regulator','regulatory','ministry','agency','permit','relations'],
  community:['community','stakeholder','grievance','social licence','local content','social'],
  esg:['esg','sustainability','materiality','governance','climate','reporting'],
  executive:['executive','board','leadership','brief','100-day','decision','ceo'],
  career:['career','job','resume','interview','speaking','recruiter'],
  guyana:['guyana','georgetown','investment','economy','local content'],
  research:['white paper','research','evidence','methodology','data']
};
function words(s){return String(s||'').toLowerCase().normalize('NFKD').replace(/[^a-z0-9\s-]/g,' ').split(/\s+/).filter(x=>x.length>1&&!STOP.has(x))}
function classify(q){
 const s=String(q||'').toLowerCase(),scores={};
 for(const [k,terms] of Object.entries(INTENTS)){let n=0;for(const t of terms)if(s.includes(t))n+=t.includes(' ')?3:1;scores[k]=n}
 return Object.entries(scores).sort((a,b)=>b[1]-a[1]).filter(x=>x[1]>0).slice(0,3).map(([intent,score])=>({intent,score}))
}
async function init(){
 if(ready)return true;
 const j=await fetch('/assets/search-index.json',{cache:'no-store'}).then(r=>r.json());
 docs=(j.documents||[]).map((d,i)=>({...d,id:i}));
 byId=new Map(docs.map(d=>[d.id,d]));
 index=new MiniSearch({
   fields:['title','description','text','type'],
   storeFields:['title','description','url','type'],
   searchOptions:{boost:{title:5,description:2.2,type:1.2},fuzzy:0.18,prefix:true,combineWith:'OR'}
 });
 index.addAll(docs);
 ready=true; return true;
}
function cleanResult(r){return {id:r.id,title:r.title,description:r.description||'',url:r.url,type:r.type||'',score:Number((r.score||0).toFixed(4)),terms:r.terms||[]}}
async function search(query,opts={}){
 await init(); const q=String(query||'').trim(); if(!q)return [];
 const limit=Math.max(1,Math.min(20,Number(opts.limit||8)));
 const res=index.search(q,{boost:{title:5,description:2.2,type:1.2},fuzzy:0.18,prefix:true,combineWith:'OR'});
 return res.slice(0,limit).map(cleanResult)
}
async function suggest(prefix){await init();return index.autoSuggest(String(prefix||''),{fuzzy:0.18,prefix:true}).slice(0,8)}
async function recommend(context={}){
 await init();
 const current=String(context.url||''),recent=Array.isArray(context.recent)?context.recent:[],seed=[context.title,context.description,context.text,...recent.map(x=>x.title||x.slug||'')].join(' ');
 const tokens=words(seed).slice(0,40),intent=classify(seed);
 let query=tokens.join(' ');
 if(intent.length)query+=' '+intent.map(x=>x.intent).join(' ');
 let res=query?index.search(query,{boost:{title:6,description:2.5,type:1.1},fuzzy:0.12,prefix:true,combineWith:'OR'}):[];
 const seen=new Set([current,...recent.slice(0,3).map(x=>x.url)]);
 const out=[];
 for(const r of res){
   if(!r.url||seen.has(r.url))continue;
   let score=r.score||0;
   for(const it of intent){const hay=(r.title+' '+r.description+' '+r.type).toLowerCase();if(hay.includes(it.intent))score+=it.score*2}
   out.push({...cleanResult(r),score:Number(score.toFixed(4))});
   if(out.length>=5)break;
 }
 return {intent,recommendations:out}
}
async function contextFor(query,limit=6){const results=await search(query,{limit});return results.map((r,i)=>({n:i+1,title:r.title,url:r.url,description:r.description,type:r.type}))}
Comlink.expose({init,search,suggest,recommend,classify,contextFor});
