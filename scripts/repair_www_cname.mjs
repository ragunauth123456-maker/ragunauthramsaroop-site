#!/usr/bin/env node
/**
 * Owner-authorized repair for the public www CNAME used by GitHub Pages.
 * This script changes one registrar record only:
 *   www: ragunauth123456-maker.github.io -> ragunauthramsaroop.github.io
 * It verifies the apex GitHub Pages A records first and stops on any unexpected DNS state.
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

async function main(){
  let records=await list();
  assertApexIntact(records);

  const atWww=wwwRecords(records);
  const nonCname=atWww.filter(r=>r.type!=="CNAME");
  if(nonCname.length) throw Error("Unexpected non-CNAME record exists at www. Stopping without changes.");

  const cnames=atWww.filter(r=>r.type==="CNAME");
  if(cnames.length!==1) throw Error("Expected exactly one registrar CNAME at www. Found "+cnames.length+". Stopping.");

  const current=lower(cnames[0].cname);
  if(current===NEW){
    console.log("PASS: www CNAME is already correct: "+NEW);
    return;
  }
  if(current!==OLD){
    throw Error("Unexpected www CNAME target "+current+". Stopping without changes.");
  }

  console.log("Verified apex GitHub Pages A records.");
  console.log("Replacing stale www CNAME "+OLD+" with "+NEW+".");

  await spaceship("DELETE",[{type:"CNAME",name:"www",cname:cnames[0].cname}]);
  await spaceship("PUT",{force:false,items:[{type:"CNAME",name:"www",cname:NEW,ttl:300}]});

  records=await list();
  assertApexIntact(records);
  const after=wwwRecords(records).filter(r=>r.type==="CNAME");
  if(after.length!==1 || lower(after[0].cname)!==NEW){
    throw Error("Registrar verification failed after update.");
  }
  console.log("PASS: Spaceship registrar now returns www CNAME "+NEW+".");
  console.log("No other DNS records were changed.");
}

main().catch(err=>{
  console.error("WWW DNS REPAIR FAILED: "+err.message);
  process.exitCode=1;
});
