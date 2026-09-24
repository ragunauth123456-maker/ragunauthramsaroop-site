import fs from "node:fs/promises";
import path from "node:path";

const file=path.resolve("pagefind","pagefind-entry.json");
const data=JSON.parse(await fs.readFile(file,"utf8"));
if(data.languages && typeof data.languages==="object"){
  data.languages=Object.fromEntries(Object.entries(data.languages).sort(([a],[b])=>a.localeCompare(b)));
}
await fs.writeFile(file,JSON.stringify(data));
console.log("normalized",file);
