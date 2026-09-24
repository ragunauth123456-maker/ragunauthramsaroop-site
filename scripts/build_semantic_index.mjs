import fs from "node:fs/promises";
import path from "node:path";
import { pipeline } from "@huggingface/transformers";

const root = path.resolve(".");
const input = JSON.parse(await fs.readFile(path.join(root,"assets","search-index.json"),"utf8"));
const docs = (input.documents || []).filter(d => d && d.url && d.title);
const model = "Xenova/all-MiniLM-L6-v2";
console.log("Loading",model,"for",docs.length,"documents");
const extractor = await pipeline("feature-extraction", model, { dtype: "q8" });

function compactText(d){
  const text = String(d.text||"").replace(/\s+/g," ").trim();
  return [d.title,d.description||"",text.slice(0,1200)].filter(Boolean).join(" | ");
}
function quantize(values){
  let max=0; for(const v of values) max=Math.max(max,Math.abs(v));
  const scale=max?max/127:1/127;
  const q=new Int8Array(values.length);
  for(let i=0;i<values.length;i++) q[i]=Math.max(-127,Math.min(127,Math.round(values[i]/scale)));
  return {scale,q:Buffer.from(q.buffer,q.byteOffset,q.byteLength).toString("base64")};
}
const output=[];
const batchSize=16;
for(let i=0;i<docs.length;i+=batchSize){
  const batch=docs.slice(i,i+batchSize);
  const texts=batch.map(compactText);
  const emb=await extractor(texts,{pooling:"mean",normalize:true});
  const dims=emb.dims;
  const width=dims[dims.length-1];
  const data=emb.data;
  for(let j=0;j<batch.length;j++){
    const values=Array.from(data.slice(j*width,(j+1)*width));
    const {scale,q}=quantize(values);
    const d=batch[j];
    output.push({url:d.url,title:d.title,description:d.description||"",type:d.type||"Public",scale,q});
  }
  console.log("embedded",Math.min(i+batch.length,docs.length),"/",docs.length);
}
const payload={version:1,generated:String(input.updated||"source-index"),model,dimensions:384,quantization:"int8-per-vector-scale",documents:output};
await fs.writeFile(path.join(root,"assets","semantic-index.json"),JSON.stringify(payload));
console.log("wrote assets/semantic-index.json",output.length,"documents");
