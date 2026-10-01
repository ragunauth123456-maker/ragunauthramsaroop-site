(function(){
  "use strict";

  const form = document.getElementById("research-question-form");
  const question = document.getElementById("research-question");
  const mode = document.getElementById("research-mode");
  const submit = document.getElementById("research-submit");
  const status = document.getElementById("research-status");
  const answer = document.getElementById("research-answer");
  const sources = document.getElementById("research-sources");
  const sourceList = document.getElementById("research-source-list");
  const confidence = document.getElementById("research-confidence");
  const researchActions = document.getElementById("research-actions");
  const exampleButtons = document.querySelectorAll("[data-question]");
  let gatewayConfigPromise = null;

  if(!form || !question || !mode || !submit || !status || !answer || !sources || !sourceList || !confidence) return;

  function setBusy(isBusy){
    submit.disabled = isBusy;
    submit.textContent = isBusy ? "Searching research..." : "Search published research";
    form.setAttribute("aria-busy", isBusy ? "true" : "false");
  }

  function clearResult(){
    answer.hidden = true;
    sources.hidden = true;
    answer.textContent = "";
    sourceList.replaceChildren();
    if(researchActions) researchActions.hidden = true;
  }

  function sourceItem(source){
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = source.href;
    a.textContent = source.label;
    li.appendChild(a);
    return li;
  }

  function confidenceLabel(result){
    const value = String(result && result.confidence || "").toLowerCase();
    const prefix = result && result.ai_assisted ? "AI + " : "";
    if(value === "high") return prefix + "Strong match";
    if(value === "medium") return prefix + "Good match";
    if(value === "low") return prefix + "Limited match";
    return result && result.sources && result.sources.length ? prefix + "Evidence match" : "No match";
  }

  async function loadGatewayConfig(){
    if(gatewayConfigPromise) return gatewayConfigPromise;
    gatewayConfigPromise = fetch("/assets/research-gateway-config.json",{cache:"no-store"})
      .then(function(response){ return response.ok ? response.json() : null; })
      .then(function(config){
        if(!config || config.enabled !== true) return null;
        const endpoint = String(config.endpoint || "").trim();
        if(!/^https:\/\//i.test(endpoint)) return null;
        return {
          endpoint:endpoint,
          timeoutMs:Math.max(3000,Math.min(30000,Number(config.timeoutMs)||12000))
        };
      })
      .catch(function(){ return null; });
    return gatewayConfigPromise;
  }

  async function askGateway(text,lens){
    const config = await loadGatewayConfig();
    if(!config) return null;
    const controller = new AbortController();
    const timer = setTimeout(function(){ controller.abort(); },config.timeoutMs);
    try{
      const response = await fetch(config.endpoint,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({question:text,mode:lens}),
        signal:controller.signal,
        credentials:"omit",
        referrerPolicy:"strict-origin-when-cross-origin"
      });
      if(!response.ok) throw new Error("gateway_unavailable");
      const result = await response.json();
      if(!result || typeof result.answer !== "string" || !Array.isArray(result.sources)) throw new Error("gateway_invalid");
      return result;
    }finally{
      clearTimeout(timer);
    }
  }

  async function askLocal(text,lens){
    if(typeof window.RRResearchAsk !== "function") throw new Error("local_index_unavailable");
    return window.RRResearchAsk({question:text,mode:lens});
  }

  function saveResearchHandoff(text,result){
    try{
      const safeSources = (Array.isArray(result.sources) ? result.sources : []).slice(0,5).map(function(item){
        return {label:String(item.label||"Published source").slice(0,140),href:String(item.href||"/research-library/").slice(0,240)};
      });
      sessionStorage.setItem("rrResearchHandoff",JSON.stringify({
        question:text.slice(0,700),
        answer:String(result.answer||"").slice(0,1800),
        sources:safeSources,
        mode:mode.value,
        createdAt:Date.now()
      }));
      return true;
    }catch(_){
      return false;
    }
  }

  async function runResearchQuery(){
    const text = question.value.trim();
    if(text.length < 4){
      status.textContent = "Enter a fuller question so the evidence search has enough context.";
      confidence.textContent = "Needs detail";
      clearResult();
      question.focus();
      return;
    }

    setBusy(true);
    clearResult();
    status.textContent = "Searching the approved public research index.";
    confidence.textContent = "Searching";

    try{
      let result = null;
      try{
        result = await askGateway(text,mode.value);
      }catch(_){
        result = null;
      }
      if(!result) result = await askLocal(text,mode.value);

      if(result.ai_assisted){
        status.textContent = "AI-assisted response grounded in approved published evidence. Supporting sources remain visible below.";
      }else{
        status.textContent = "Response grounded in the closest matching published material.";
      }

      answer.textContent = result.answer || "No answer was returned.";
      answer.hidden = false;

      const items = Array.isArray(result.sources) ? result.sources : [];
      items.forEach(function(item){ sourceList.appendChild(sourceItem(item)); });
      sources.hidden = items.length === 0;
      confidence.textContent = confidenceLabel(result);
      if(researchActions) researchActions.hidden = !saveResearchHandoff(text,result);
    }catch(_){
      status.textContent = "The research service is unavailable right now. Open the research library for direct access to the publications.";
      confidence.textContent = "Unavailable";
      clearResult();
    }finally{
      setBusy(false);
    }
  }

  form.addEventListener("submit", function(event){
    event.preventDefault();
    runResearchQuery();
  });

  exampleButtons.forEach(function(button){
    button.addEventListener("click", function(){
      question.value = button.getAttribute("data-question") || "";
      question.focus();
      runResearchQuery();
    });
  });

  const params = new URLSearchParams(location.search);
  const incoming = params.get("q");
  if(incoming){
    question.value = incoming.slice(0,700);
    runResearchQuery();
  }else if(params.get("from")==="guyana"){
    try{
      const raw = sessionStorage.getItem("rrGuyanaQuestion");
      const handoff = raw ? JSON.parse(raw) : null;
      if(handoff && handoff.question && handoff.createdAt && Date.now()-Number(handoff.createdAt)<7200000){
        question.value = String(handoff.question).slice(0,700);
        sessionStorage.removeItem("rrGuyanaQuestion");
        runResearchQuery();
      }
    }catch(_){}
  }
})();