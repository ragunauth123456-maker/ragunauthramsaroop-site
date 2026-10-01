const fs=require("fs");
const assert=require("assert");

const data=JSON.parse(fs.readFileSync("assets/guyana-intelligence-data.json","utf8"));
const html=fs.readFileSync("guyana-intelligence/index.html","utf8");
const js=fs.readFileSync("assets/guyana-intelligence.js","utf8");
const ask=fs.readFileSync("assets/ask-research-ui.js","utf8");
const home=fs.readFileSync("index.html","utf8");

assert.ok(Array.isArray(data.sectors),"sectors must be an array");
assert.ok(data.sectors.length>=8,"expected at least eight Guyana sector pathways");

const ids=data.sectors.map(x=>x.id);
assert.equal(new Set(ids).size,ids.length,"sector ids must be unique");
for(const required of ["mining","energy","investment","infrastructure","environment","institutions","strategy","water"]){
  assert.ok(ids.includes(required),"missing sector "+required);
}

for(const sector of data.sectors){
  assert.ok(sector.label&&sector.summary,"sector requires label and summary");
  assert.ok(Array.isArray(sector.questions)&&sector.questions.length>=3,sector.id+" requires at least three decision questions");
  assert.ok(Array.isArray(sector.tools)&&sector.tools.length>=3,sector.id+" requires at least three tools");
  assert.ok(Array.isArray(sector.research)&&sector.research.length>=3,sector.id+" requires at least three research links");
  assert.ok(Array.isArray(sector.sources)&&sector.sources.length>=2,sector.id+" requires at least two public-source starting points");
  sector.tools.concat(sector.research).forEach(item=>{
    assert.ok(String(item.href||"").startsWith("/"),sector.id+" internal link must be site-relative");
  });
  sector.sources.forEach(item=>{
    const href=String(item.href||"");
    assert.ok(href.startsWith("/")||href.startsWith("https://"),sector.id+" source link must be internal or HTTPS");
  });
}

for(const id of ["sector-buttons","sector-questions","sector-sources","sector-research","sector-tools","guyana-ask-form","gy-results"]){
  assert.ok(html.includes('id="'+id+'"'),"missing page element "+id);
}
assert.ok(html.includes("/assets/guyana-intelligence.js"),"page must load Guyana intelligence script");
assert.ok(js.includes('sessionStorage.setItem("rrGuyanaQuestion"'),"Guyana question handoff must use session storage");
assert.ok(!js.includes("?q="),"Guyana question must not be placed in a query-string q parameter");
assert.ok(ask.includes('sessionStorage.getItem("rrGuyanaQuestion"'),"Ask Research must consume Guyana session handoff");
assert.ok(home.includes('href="/guyana-intelligence/"'),"homepage must link to Guyana Intelligence Centre");

console.log("PASS: Guyana Intelligence Centre structure, source paths and private research handoff");
