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
  const exampleButtons = document.querySelectorAll("[data-question]");

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
    if(value === "high") return "Strong match";
    if(value === "medium") return "Good match";
    if(value === "low") return "Limited match";
    return result && result.sources && result.sources.length ? "Evidence match" : "No match";
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

    if(typeof window.RRResearchAsk !== "function"){
      status.textContent = "The research index did not load. Open the research library directly while the assistant reloads.";
      confidence.textContent = "Unavailable";
      clearResult();
      return;
    }

    setBusy(true);
    clearResult();
    status.textContent = "Searching the approved public research index.";
    confidence.textContent = "Searching";

    try{
      const result = await window.RRResearchAsk({question:text, mode:mode.value});
      status.textContent = "Response grounded in the closest matching published material.";
      answer.textContent = result.answer || "No answer was returned.";
      answer.hidden = false;

      const items = Array.isArray(result.sources) ? result.sources : [];
      items.forEach(item => sourceList.appendChild(sourceItem(item)));
      sources.hidden = items.length === 0;
      confidence.textContent = confidenceLabel(result);
    }catch(err){
      status.textContent = "The local research index is unavailable right now. Open the research library for direct access to the publications.";
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
  }
})();