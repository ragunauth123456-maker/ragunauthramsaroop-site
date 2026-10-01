/* Browser-side evidence search. No external model, account or paid API required. */
(function(){
  "use strict";

  let cache=null;
  const STOP=new Set("the a an and or but if then of to in on for with by from as at is are was were be been being this those these what how who why when where does do did should would about give tell show explain his he him randy ragunauth into across through".split(" "));
  const SYN={
    esg:["sustainability","environmental","social","governance"],
    sustainability:["esg","environmental","social","governance"],
    government:["institutional","regulatory","public affairs","state"],
    regulator:["government","regulatory","institutional"],
    regulation:["regulatory","government","compliance"],
    mining:["gold","natural resources","mine","minerals"],
    mineral:["mining","critical minerals","supply chain"],
    minerals:["mining","critical minerals","supply chain"],
    energy:["renewable","power","electricity","solar","generation"],
    electricity:["energy","power","generation","grid"],
    power:["energy","electricity","generation","grid"],
    climate:["carbon","forest","transition","resilience"],
    carbon:["climate","forest","credits","emissions"],
    water:["resilience","infrastructure","security","freshwater"],
    leadership:["executive","director","management","governance"],
    career:["professional","experience","record","executive"],
    community:["social","stakeholder","grievance","licence"],
    stakeholder:["community","social","trust","engagement"],
    compliance:["governance","regulatory","ethics","controls"],
    trust:["institutional","stakeholder","governance","social licence"],
    economy:["economic","development","finance","growth"],
    finance:["investment","capital","economic","development"],
    guyana:["national","georgetown","development","state"],
    ai:["artificial intelligence","compute","chips","data centres","sovereign"],
    biodiversity:["nature","forest","conservation","30x30"],
    supply:["supply chain","resilience","minerals","trade"],
    transition:["energy transition","renewable","climate","power"]
  };

  const norm=s=>String(s||"").toLowerCase().normalize("NFKD").replace(/[^\w\s-]/g," ").replace(/\s+/g," ").trim();

  const words=s=>{
    const base=norm(s).split(" ").filter(w=>w.length>2&&!STOP.has(w));
    const out=new Set(base);
    base.forEach(w=>(SYN[w]||[]).forEach(x=>out.add(x)));
    return [...out];
  };

  async function load(){
    if(cache)return cache;
    const response=await fetch("/assets/research-index.json",{cache:"force-cache"});
    if(!response.ok)throw new Error("Evidence index unavailable");
    cache=await response.json();
    return cache;
  }

  function sentences(text){
    return String(text||"").split(/(?<=[.!?])\s+/).map(s=>s.trim()).filter(s=>s.length>45&&s.length<520);
  }

  function rankDoc(doc,terms,question){
    const title=norm(doc.title);
    const body=norm(doc.text);
    const category=norm(doc.category||"");
    const q=norm(question);
    let score=0;

    if(q.length>5&&title.includes(q))score+=35;
    terms.forEach(t=>{
      if(title.includes(t))score+=12;
      if(category.includes(t))score+=7;
      const count=body.split(t).length-1;
      score+=Math.min(count,7)*2;
    });
    return score;
  }

  function sentenceScore(sentence,terms){
    const n=norm(sentence);
    let score=0;
    terms.forEach(t=>{if(n.includes(t))score+=4});
    return score;
  }

  function confidence(topScore,terms){
    const adjusted=topScore+Math.min(terms.length,8);
    if(adjusted>=32)return "high";
    if(adjusted>=17)return "medium";
    return "low";
  }

  window.RRResearchAsk=async function(payload){
    const question=String(payload&&payload.question||"").trim();
    const mode=String(payload&&payload.mode||"general");

    if(question.length<4){
      return {answer:"Please enter a fuller question about the published research or public professional record.",sources:[],confidence:"low"};
    }

    const data=await load();
    const terms=words(question);
    const ranked=data.documents
      .map(d=>({d,score:rankDoc(d,terms,question)}))
      .filter(x=>x.score>0)
      .sort((a,b)=>b.score-a.score)
      .slice(0,6);

    if(!ranked.length){
      return {
        answer:"I did not find a confident match in the approved public research index. Try a more specific question about ESG, mining, energy, Guyana, corporate affairs, government relations, leadership, water, climate, critical minerals, finance or governance.",
        sources:[
          {label:"Executive profile",href:"/executive-profile/"},
          {label:"Research library",href:"/research-library/"},
          {label:"Public tools",href:"/tools/"}
        ],
        confidence:"low"
      };
    }

    const candidates=[];
    ranked.forEach(({d,score})=>{
      sentences(d.text).forEach(s=>candidates.push({s,d,score:score+sentenceScore(s,terms)}));
    });
    candidates.sort((a,b)=>b.score-a.score);

    const picked=[];
    const used=new Set();
    for(const candidate of candidates){
      const key=norm(candidate.s).slice(0,140);
      if(used.has(key))continue;
      used.add(key);
      picked.push(candidate);
      if(picked.length>=4)break;
    }

    const lens={
      recruiter:"From an executive-search perspective, ",
      board:"From a board or advisory perspective, ",
      institutional:"From an institutional perspective, ",
      media:"For media or public-context use, ",
      general:""
    };

    let answer=(lens[mode]||"")+"the strongest matching evidence in the published record is: ";
    answer+=picked.map(x=>x.s).join(" ");
    answer=answer.slice(0,1650);

    const sources=[];
    const seen=new Set();
    ranked.forEach(({d})=>{
      if(!seen.has(d.href)&&sources.length<5){
        seen.add(d.href);
        sources.push({
          label:d.title.replace(/\s*\|\s*Ragunauth.*$/i,"").slice(0,110),
          href:d.href
        });
      }
    });

    return {
      answer,
      sources,
      confidence:confidence(ranked[0].score,terms),
      matchedTerms:terms.slice(0,10)
    };
  };
})();