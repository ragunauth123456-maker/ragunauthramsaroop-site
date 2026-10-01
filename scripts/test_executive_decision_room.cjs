const fs=require("fs");
const assert=require("assert");

const page=fs.readFileSync("decision-room/index.html","utf8");
const js=fs.readFileSync("assets/decision-room.js","utf8");
const briefing=fs.readFileSync("guyana-briefing/index.html","utf8");
const briefingJs=fs.readFileSync("assets/guyana-daily-briefing.js","utf8");
const research=fs.readFileSync("ask-research/index.html","utf8");
const observatory=fs.readFileSync("observatory/index.html","utf8");
const observatoryJs=fs.readFileSync("assets/observatory-sector-briefs.js","utf8");
const guyana=fs.readFileSync("guyana-intelligence/index.html","utf8");

for(const id of [
  "dr-title","dr-owner","dr-date","dr-status","dr-evidence-state","dr-facts","dr-unknowns",
  "dr-stakeholders","dr-risks","dr-options","dr-criteria","dr-recommendation","dr-actions",
  "dr-import-context","dr-import","dr-build","dr-print","dr-share","dr-clear",
  "dr-evidence-ledger","dr-completeness","dr-pack"
]){
  assert.ok(page.includes('id="'+id+'"'),"missing Decision Room element "+id);
}
assert.ok(page.includes("0/11 fields populated"),"Decision Room completion counter must start at 0/11");
assert.ok(page.includes("shareable URL stores the current pack inside the URL fragment"),"share privacy warning must be visible");
assert.ok(page.includes("/assets/decision-room-executive.css"),"executive Decision Room stylesheet must load");

assert.ok(js.includes('const STORAGE_KEY="rrDecisionRoomV2"'),"Decision Room must use the v2 local browser workspace");
assert.ok(js.includes('sessionStorage.getItem("rrResearchHandoff"'),"Decision Room must import research and briefing session context");
assert.ok(js.includes('sessionStorage.getItem("rrDecisionRoomImport"'),"Decision Room must support a dedicated session import");
assert.ok(js.includes("function renderLedger()"),"Decision Room must render an evidence ledger");
assert.ok(js.includes("function topicQuestions("),"Decision Room must generate board scrutiny questions");
assert.ok(js.includes("Pack too large for review URL"),"Decision Room must guard oversized share links");
assert.ok(js.includes('"#review="+enc(state())'),"shareable review data must use the URL fragment");
assert.ok(!js.includes("fetch("),"Decision Room must not send workspace data to a network endpoint");
assert.ok(js.includes('localStorage.removeItem(STORAGE_KEY)'),"Decision Room must provide workspace clearing");

assert.ok(briefing.includes('id="brief-decision"'),"daily briefing must expose a Decision Room action");
assert.ok(briefingJs.includes('location.href="/decision-room/?from=briefing"'),"daily briefing must hand off privately to Decision Room");
assert.ok(research.includes('id="research-decision-link"'),"Ask Research must expose a Decision Room action");
assert.ok(research.includes('href="/decision-room/?from=research"'),"Ask Research Decision Room route must be explicit");
assert.ok(observatory.includes('id="obs-sector-decision"'),"Observatory sector board must expose Decision Room");
assert.ok(observatoryJs.includes('location.href="/decision-room/?from=observatory"'),"Observatory must hand off to Decision Room");
assert.ok(guyana.includes('href="/decision-room/"'),"Guyana Intelligence must link to Decision Room");

console.log("PASS: Executive Decision Room imports, evidence ledger, private workspace and connected handoffs");
