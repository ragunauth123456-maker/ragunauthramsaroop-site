/* Browser-side evidence search. No AppDeploy API, account or paid model required. */
(function(){
  "use strict";
  let cache=null;
  const STOP=new Set("the a an and or but if then of to in on for with by from as at is are was were be been being this that these those what how who why when where does do did can could should would about give tell show explain his he him randy ragunauth".split(" "));
  const SYN={esg:["sustainability","environmental","social","governance"],government:["institutional","regulatory","public affairs"],mining:["gold","natural resources","mine"],energy:["renewable","power","solar"],leadership:["executive","director","management"],career:["professional","experience","record"],community:["social","stakeholder","grievance"],compliance:["governance","regulatory","ethics"]};
  const norm=s=>String(s||"").toLowerCase().normalize("NFKD").replace(/[^\w\s-]/g," ").replace(/\s+/g," ").trim();
  const words=s=>{
    const base=norm(s).split(" ").filter(w=>w.length>2&&!STOP.has(w));
    const out=new Set(base);
    base.forEach(w=>(SYN[w]||[]).forEach(x=>out.add(x)));
    return [...out];
  };
  async function load(){
    if(cache)return cache;
    const r=await fetch("/assets/research-index.json",{cache:"force-cache"});
    if(!r.ok)throw new Error("Evidence index unavailable");
    cache=await r.json(); return cache;
  }
  function sentences(text){
    return String(text||"").split(/(?<=[.!?])\s+/).map(s=>s.trim()).filter(s=>s.length>45&&s.length<460);
  }
  function rankDoc(doc,terms){
    const title=norm(doc.title), body=norm(doc.text); let score=0;
    terms.forEach(t=>{ if(title.includes(t))score+=12; const n=body.split(t).length-1; score+=Math.min(n,6)*2; });
    return score;
  }
  function sentenceScore(s,terms){
    const n=norm(s); let score=0; terms.forEach(t=>{if(n.includes(t))score+=4}); return score;
  }
  window.RRResearchAsk=async function(payload){
    const question=String(payload&&payload.question||"").trim(), mode=String(payload&&payload.mode||"general");
    if(question.length<4) return {answer:"Please enter a fuller question about the public professional record.",sources:[]};
    const data=await load(), terms=words(question);
    const ranked=data.documents.map(d=>({d,score:rankDoc(d,terms)})).filter(x=>x.score>0).sort((a,b)=>b.score-a.score).slice(0,5);
    if(!ranked.length){
      return {answer:"I could not match that question confidently to the approved public record. Try a more specific question about ESG, mining, energy, corporate affairs, government relations, leadership, awards, research or career experience.",sources:[
        {label:"Executive profile",href:"/executive-profile/"},
        {label:"Research library",href:"/white-papers/"},
        {label:"Case studies",href:"/case-studies/"}
      ]};
    }
    const candidates=[];
    ranked.forEach(({d,score})=>sentences(d.text).forEach(s=>candidates.push({s,d,score:score+sentenceScore(s,terms)})));
    candidates.sort((a,b)=>b.score-a.score);
    const picked=[]; const used=new Set();
    for(const c of candidates){
      const key=norm(c.s).slice(0,120);
      if(used.has(key))continue;
      used.add(key); picked.push(c); if(picked.length>=4)break;
    }
    const lens={recruiter:"From an executive-search perspective, ",board:"From a board or advisory perspective, ",institutional:"From an institutional perspective, ",media:"For media or public-context use, ",general:""};
    let answer=(lens[mode]||"")+"the strongest matching evidence in the published record is: ";
    answer+=picked.map(x=>x.s).join(" ");
    answer=answer.slice(0,1450);
    const sources=[]; const seen=new Set();
    ranked.forEach(({d})=>{if(!seen.has(d.href)&&sources.length<4){seen.add(d.href);sources.push({label:d.title.replace(/\s*\|\s*Ragunauth.*$/i,"").slice(0,90),href:d.href})}});
    return {answer,sources};
  };
})();