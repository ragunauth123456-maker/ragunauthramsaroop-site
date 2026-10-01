const fs = require("fs");
const vm = require("vm");

const index = JSON.parse(fs.readFileSync("assets/research-index.json","utf8"));
const source = fs.readFileSync("assets/research-assistant.js","utf8");

const context = {
  window: {},
  fetch: async () => ({ok:true,json:async()=>index}),
  console
};
vm.createContext(context);
vm.runInContext(source,context,{filename:"assets/research-assistant.js"});

async function check(question, expectedFragment){
  const result = await context.window.RRResearchAsk({question,mode:"general"});
  if(!result || !Array.isArray(result.sources) || result.sources.length === 0){
    throw new Error("No sources returned for: "+question);
  }
  if(!result.sources.some(s => String(s.href||"").includes(expectedFragment))){
    throw new Error("Expected source "+expectedFragment+" for: "+question+"\nReturned: "+JSON.stringify(result.sources));
  }
  if(!["high","medium","low"].includes(result.confidence)){
    throw new Error("Missing confidence label for: "+question);
  }
}

(async()=>{
  await check("What does the research say about Guyana electricity demand and energy security through 2030?","guyana-power-demand-2030");
  await check("What are the main strategic risks in critical mineral supply chains?","critical-minerals-energy-security");
  await check("How should mining companies think about stakeholder trust and social licence?","case-studies");
  console.log("PASS: research assistant returned expected grounded sources");
})().catch(err=>{
  console.error("FAIL:",err.message);
  process.exit(1);
});