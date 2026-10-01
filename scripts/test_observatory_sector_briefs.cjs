const fs=require("fs");
const assert=require("assert");

const cfg=JSON.parse(fs.readFileSync("assets/observatory-sector-briefs.json","utf8"));
const html=fs.readFileSync("observatory/index.html","utf8");
const js=fs.readFileSync("assets/observatory-sector-briefs.js","utf8");
const tools=fs.readFileSync("tools/assets/tools.js","utf8");

assert.ok(Array.isArray(cfg.sectors),"sectors must be an array");
assert.ok(cfg.sectors.length>=6,"expected at least six sector briefing boards");
const required=["mining","energy","investment","infrastructure","environment","strategy"];
const ids=cfg.sectors.map(x=>x.id);
required.forEach(id=>assert.ok(ids.includes(id),"missing sector "+id));
assert.equal(new Set(ids).size,ids.length,"sector ids must be unique");

for(const sector of cfg.sectors){
  assert.ok(sector.label&&sector.summary,sector.id+" requires label and summary");
  assert.ok(Array.isArray(sector.indicators)&&sector.indicators.length>=3,sector.id+" requires at least three indicators");
  assert.ok(Array.isArray(sector.watch)&&sector.watch.length>=3,sector.id+" requires at least three source links");
  assert.ok(Array.isArray(sector.questions)&&sector.questions.length>=3,sector.id+" requires decision questions");
  assert.ok(Array.isArray(sector.research)&&sector.research.length>=2,sector.id+" requires research links");
  sector.indicators.forEach(item=>assert.ok(/^[A-Z0-9.]+$/.test(item.code),sector.id+" has invalid indicator code"));
  sector.watch.forEach(item=>assert.ok(String(item.url).startsWith("https://"),sector.id+" source must use HTTPS"));
  sector.research.forEach(item=>assert.ok(String(item.href).startsWith("/"),sector.id+" research link must be site-relative"));
}

for(const id of ["obs-sector-tabs","obs-sector-title","obs-sector-metrics","obs-sector-questions","obs-sector-sources","obs-sector-research","obs-sector-ask","obs-sector-brief"]){
  assert.ok(html.includes('id="'+id+'"'),"missing Observatory sector element "+id);
}
assert.ok(html.includes("/assets/observatory-sector-briefs.js"),"sector briefing script must load");
assert.ok(html.includes("/assets/observatory-sector-briefs.css"),"sector briefing stylesheet must load");
assert.ok(js.includes('sessionStorage.setItem("rrGuyanaQuestion"'),"research handoff must stay in browser session storage");
assert.ok(js.includes('sessionStorage.setItem("rrResearchHandoff"'),"executive brief handoff must stay in browser session storage");
assert.ok(!js.includes("?q="),"sector brief must not put questions into a q query parameter");
assert.ok(tools.includes("Imported from the Guyana Observatory."),"executive brief must label Observatory imports accurately");

console.log("PASS: Observatory sector briefings, official-source paths and private handoffs");
