#!/usr/bin/env node
/**
 * Owner-authorized self-healing DNS guard for the GitHub Pages www hostname.
 *
 * Allowed automatic changes are intentionally narrow:
 * 1. Add www -> ragunauthramsaroop.github.io when www CNAME is missing and no
 *    other record occupies www.
 * 2. Replace the retired www target ragunauth123456-maker.github.io with the
 *    current GitHub Pages target.
 *
 * Any unexpected www target, extra www record, or change to the approved four
 * apex GitHub Pages A records causes a hard stop with no automatic overwrite.
 */
const ROOT="ragunauthramsaroop.com";
const API="https://spaceship.dev/api/v1/dns/records/"+encodeURIComponent(ROOT);
const OLD="ragunauth123456-maker.github.io";
const NEW="ragunauthramsaroop.github.io";
const EXPECTED_A=["185.199.108.153","185.199.109.153","185.199.110.153","185.199.111.153"].sort();

const lower=v=>String(v??"").trim().toLowerCase().replace(/\.$/,"");
const sorted=a=>[...a].map(lower).sort();

async function spaceship(method, body){
  const key=process.env.SPACESHIP_API_KEY;
  const secret=process.env.SPACESHIP_API_SECRET;
  if(!key||!secret) throw Error("Required Spaceship GitHub Actions secrets are not configured");
  const response=await fetch(API+(method==="GET"?"?take=500&skip=0":""),{
    method,
    headers:{
      "X-API-Key":key,
      "X-API-Secret":secret,
      "Accept":"application/json",
      ...(body?{"Content-Type":"application/json"}:{})
    },
    ...(body?{body:JSON.stringify(body)}:{}),
    signal:AbortSignal.timeout(20000)
  });
  if(!response.ok){
    const detail=await response.text().catch(()=>"");
    throw Error("Spaceship API "+method+" failed with HTTP "+response.status+(detail?": "+detail:""));
  }
  if(response.status===204) return null;
  return response.json();
}

async function list(){
  const payload=await spaceship("GET");
  if(!payload||!Array.isArray(payload.items)) throw Error("Unexpected Spaceship DNS response");
  return payload.items;
}

function assertApexIntact(records){
  const apexA=records
    .filter(r=>r.type==="A" && lower(r.name)==="@")
    .map(r=>r.address);
  if(JSON.stringify(sorted(apexA))!==JSON.stringify(EXPECTED_A)){
    throw Error("Apex GitHub Pages A records differ from the approved four-record set. Stopping without changes.");
  }
}

function wwwRecords(records){
  return records.filter(r=>lower(r.name)==="www");
}

async function verify(){
  const records=await list();
  assertApexIntact(records);
  const atWww=wwwRecords(records);
  const nonCname=atWww.filter(r=>r.type!=="CNAME");
  if(nonCname.length) throw Error("Unexpected non-CNAME record exists at www. Stopping without changes.");
  const cnames=atWww.filter(r=>r.type==="CNAME");
  if(cnames.length!==1 || lower(cnames[0].cname)!==NEW){
    throw Error("Registrar verification failed. Expected exactly one www CNAME to "+NEW+".");
  }
  return records;
}

async function main(){
  let records=await list();
  assertApexIntact(records);

  const atWww=wwwRecords(records);
  const nonCname=atWww.filter(r=>r.type!=="CNAME");
  if(nonCname.length) throw Error("Unexpected non-CNAME record exists at www. Stopping without changes.");

  const cnames=atWww.filter(r=>r.type==="CNAME");
  if(cnames.length>1) throw Error("More than one www CNAME exists. Stopping without changes.");

  if(cnames.length===0){
    console.log("www CNAME is missing. Restoring approved GitHub Pages target "+NEW+".");
    await spaceship("PUT",{force:false,items:[{type:"CNAME",name:"www",cname:NEW,ttl:300}]});
    await verify();
    console.log("PASS: Missing www CNAME restored to "+NEW+".");
    console.log("No unrelated DNS records were changed.");
    return;
  }

  const current=lower(cnames[0].cname);
  if(current===NEW){
    console.log("PASS: www CNAME is already correct: "+NEW);
    return;
  }

  if(current!==OLD){
    throw Error("Unexpected www CNAME target "+current+". Automatic overwrite refused.");
  }

  console.log("Replacing retired www CNAME "+OLD+" with "+NEW+".");
  await spaceship("DELETE",[{type:"CNAME",name:"www",cname:cnames[0].cname}]);
  await spaceship("PUT",{force:false,items:[{type:"CNAME",name:"www",cname:NEW,ttl:300}]});
  await verify();

  console.log("PASS: Spaceship registrar returns www CNAME "+NEW+".");
  console.log("No unrelated DNS records were changed.");
}

main().catch(err=>{
  console.error("WWW DNS GUARD FAILED: "+err.message);
  process.exitCode=1;
});
