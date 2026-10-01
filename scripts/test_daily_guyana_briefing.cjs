const fs=require("fs");
const assert=require("assert");

const page=fs.readFileSync("guyana-briefing/index.html","utf8");
const js=fs.readFileSync("assets/guyana-daily-briefing.js","utf8");
const sources=JSON.parse(fs.readFileSync("data/source-sources.json","utf8"));
const workflow=fs.readFileSync(".github/workflows/daily-guyana-intelligence.yml","utf8");
const resourceIndex=JSON.parse(fs.readFileSync("assets/resource-index.json","utf8"));
const sitemap=fs.readFileSync("sitemap.xml","utf8");
const guyana=fs.readFileSync("guyana-intelligence/index.html","utf8");
const observatory=fs.readFileSync("observatory/index.html","utf8");
const tools=fs.readFileSync("tools/assets/tools.js","utf8");

for(const id of [
  "brief-freshness","brief-source-count","brief-change-count","brief-indicator-count",
  "brief-sector-count","brief-executive-summary","brief-source-changes","brief-indicators",
  "brief-sectors","brief-research","brief-ask","brief-executive","brief-board","brief-print","brief-copy"
]){
  assert.ok(page.includes('id="'+id+'"'),"missing briefing element "+id);
}
assert.ok(page.includes("/assets/guyana-daily-briefing.js"),"briefing script must load");
assert.ok(page.includes("/assets/guyana-daily-briefing.css"),"briefing stylesheet must load");

assert.ok(js.includes('/data/source-monitor.json'),"briefing must use source monitor");
assert.ok(js.includes('/data/guyana-live.json'),"briefing must use dated Guyana snapshot");
assert.ok(js.includes('/assets/observatory-sector-briefs.json'),"briefing must use Observatory sector configuration");
assert.ok(js.includes('sessionStorage.setItem("rrGuyanaQuestion"'),"Ask Research handoff must use session storage");
assert.ok(js.includes('sessionStorage.setItem("rrResearchHandoff"'),"decision handoff must use session storage");
assert.ok(!js.includes("?q="),"briefing must not put research questions into q query parameters");
assert.ok(js.includes("does not by itself establish"),"briefing must preserve page-change interpretation boundary");
assert.ok(js.includes("older than 36 hours"),"briefing must warn when snapshots are stale");

assert.ok(Array.isArray(sources.sources),"source registry must contain an array");
assert.ok(sources.sources.length>=10,"daily briefing requires broader official-source coverage");
assert.equal(new Set(sources.sources.map(x=>x.url)).size,sources.sources.length,"monitored source URLs must be unique");
sources.sources.forEach(x=>{
  assert.ok(x.name&&x.category&&x.note,"each monitored source needs name, category and note");
  assert.ok(String(x.url).startsWith("https://"),"monitored sources must use HTTPS");
});

assert.ok(workflow.includes("cron: '15 10 * * *'"),"daily workflow must run at 10:15 UTC / 06:15 Guyana time");
assert.ok(/permissions:\s*\n\s*contents: write/.test(workflow),"daily workflow needs contents write permission");
assert.ok(workflow.includes("python scripts/monitor_sources.py"),"daily workflow must use the established monitor script");
for(const file of ["data/source-monitor.json","data/guyana-live.json","api/v1/sources.json","api/v1/guyana.json"]){
  assert.ok(workflow.includes(file),"daily workflow must version "+file);
}
assert.ok(workflow.includes("actions/checkout@v7"),"checkout action must satisfy repository action policy");
assert.ok(workflow.includes("actions/setup-python@v7"),"setup-python action must satisfy repository action policy");

assert.ok(resourceIndex.resources.some(x=>x.url==="/guyana-briefing/"),"resource index must include daily briefing");
assert.ok(sitemap.includes("https://ragunauthramsaroop.com/guyana-briefing/"),"sitemap must include daily briefing");
assert.ok(guyana.includes('href="/guyana-briefing/"'),"Guyana Intelligence must link to daily briefing");
assert.ok(observatory.includes('href="/guyana-briefing/"'),"Observatory must link to daily briefing");
assert.ok(tools.includes("Imported from the Executive Guyana Briefing."),"executive tools must label daily briefing handoffs accurately");

console.log("PASS: Executive Guyana Briefing structure, source discipline, daily refresh and private handoffs");
