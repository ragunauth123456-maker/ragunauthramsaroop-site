import process from 'node:process'
import { chromium } from 'playwright'

const EMAIL=process.env.SSRN_EMAIL
const PASSWORD=process.env.SSRN_PASSWORD
if(!EMAIL||!PASSWORD) throw new Error('Missing SSRN credentials')
const browser=await chromium.launch({headless:true,args:['--disable-blink-features=AutomationControlled']})
const context=await browser.newContext({viewport:{width:1440,height:1100},userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36'})
const page=await context.newPage()
page.setDefaultTimeout(30000)

async function firstVisible(loc){for(let i=0;i<await loc.count();i++){const x=loc.nth(i);if(await x.isVisible().catch(()=>false))return x}return null}
async function cookies(){
  const a=page.locator('#onetrust-accept-btn-handler')
  await a.waitFor({state:'visible',timeout:7000}).catch(()=>{})
  if(await a.isVisible().catch(()=>false)){await a.click({force:true});await page.waitForTimeout(700)}
}
async function login(){
  await page.goto('https://hq.ssrn.com/submissions/MyPapers.cfm',{waitUntil:'domcontentloaded',timeout:60000})
  await cookies()
  const pw=await firstVisible(page.locator('input[type="password"]'))
  if(!pw)return
  const em=await firstVisible(page.locator('input[placeholder*="Email" i],input[name="input-email"],input[type="email"]'))
  if(!em)throw new Error('No email field')
  await em.fill(EMAIL);await pw.fill(PASSWORD)
  await cookies()
  let b=await firstVisible(page.locator('#signinBtn'))
  if(!b)b=await firstVisible(page.getByRole('button',{name:/sign in/i}))
  if(!b)throw new Error('No sign in button')
  await b.click();await page.waitForTimeout(5000)
  if(await firstVisible(page.locator('input[type="password"]')))throw new Error('Login failed')
}
function clean(s){return String(s??'').replace(/\s+/g,' ').trim()}
async function dump(tag){
  console.log('=== '+tag+' ===')
  console.log('URL='+page.url())
  console.log('HEADINGS='+clean((await page.locator('h1,h2,h3').allTextContents().catch(()=>[])).join(' | ')))
  console.log('BODY='+clean(await page.locator('body').innerText().catch(()=> '')).slice(0,12000))
  const edits=await page.locator('[contenteditable="true"]').evaluateAll(es=>es.map((e,i)=>({i,text:(e.textContent||'').trim().slice(0,5000),id:e.id,class:e.className}))).catch(()=>[])
  console.log('EDITABLES='+JSON.stringify(edits))
  const controls=await page.locator('input,textarea,select,button').evaluateAll(es=>es.slice(0,220).map((e,i)=>({i,tag:e.tagName,type:e.getAttribute('type'),id:e.id,name:e.getAttribute('name'),placeholder:e.getAttribute('placeholder'),value:('value'in e)?e.value:null,text:(e.textContent||'').trim().slice(0,300),checked:('checked'in e)?e.checked:null,options:e.tagName==='SELECT'?Array.from(e.options).map(o=>({t:(o.textContent||'').trim(),v:o.value,sel:o.selected})).slice(0,60):null}))).catch(()=>[])
  for(const x of controls){if(x.type==='password')continue;console.log('CTRL '+JSON.stringify(x))}
}
await login()
await page.goto('https://hq.ssrn.com/submission.cfm?submission-id=20260925-200912623',{waitUntil:'domcontentloaded',timeout:60000})
await cookies()
const ct=page.locator('#trigger-input-content-type')
if(!/preprint/i.test(await ct.inputValue().catch(()=>''))){
  await ct.fill('Preprint')
  await ct.press('ArrowDown')
  await ct.press('Enter')
  await page.waitForTimeout(600)
}
let next=await firstVisible(page.getByRole('button',{name:/Next Step/i}))
if(!next)throw new Error('No Step1 next')
await next.click({force:true});await page.waitForTimeout(1600)
await dump('STEP2-BEFORE')
const date=page.locator('input[placeholder="dd/mm/yyyy"]').first()
if(await date.isVisible().catch(()=>false))await date.fill('25/09/2026')
next=await firstVisible(page.getByRole('button',{name:/Next Step/i}))
if(!next)throw new Error('No Step2 next')
await next.click({force:true});await page.waitForTimeout(2000)
await dump('AFTER-STEP2-NEXT')
await page.screenshot({path:'ssrn-stage-inspect.png',fullPage:true})
await browser.close()
