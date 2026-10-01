import process from 'node:process'
import { chromium } from 'playwright'
const EMAIL=process.env.SSRN_EMAIL, PASSWORD=process.env.SSRN_PASSWORD
if(!EMAIL||!PASSWORD)throw new Error('Missing SSRN credentials')
const browser=await chromium.launch({headless:true,args:['--disable-blink-features=AutomationControlled']})
const context=await browser.newContext({viewport:{width:1440,height:1100},userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36'})
const page=await context.newPage();page.setDefaultTimeout(30000)
async function firstVisible(loc){for(let i=0;i<await loc.count();i++){const x=loc.nth(i);if(await x.isVisible().catch(()=>false))return x}return null}
async function cookies(){const a=page.locator('#onetrust-accept-btn-handler');await a.waitFor({state:'visible',timeout:7000}).catch(()=>{});if(await a.isVisible().catch(()=>false)){await a.click({force:true});await page.waitForTimeout(700)}}
async function login(){await page.goto('https://hq.ssrn.com/submissions/MyPapers.cfm',{waitUntil:'domcontentloaded',timeout:60000});await cookies();const pw=await firstVisible(page.locator('input[type="password"]'));if(!pw)return;const em=await firstVisible(page.locator('input[name="input-email"],input[placeholder*="Email" i],input[type="email"]'));if(!em)throw new Error('No email');await em.fill(EMAIL);await pw.fill(PASSWORD);await cookies();let b=await firstVisible(page.locator('#signinBtn'));if(!b)b=await firstVisible(page.getByRole('button',{name:/sign in/i}));if(!b)throw new Error('No sign in');await b.click();await page.waitForTimeout(5000);if(await firstVisible(page.locator('input[type="password"]')))throw new Error('Login failed')}
async function clickBtn(name){const b=await firstVisible(page.getByRole('button',{name}));if(!b)throw new Error('Missing button '+name);await b.click({force:true});await page.waitForTimeout(1100)}
async function save(){await clickBtn(/^Save$/i);await page.keyboard.press('Escape').catch(()=>{});await page.waitForTimeout(350)}
function clean(s){return String(s??'').replace(/\s+/g,' ').trim()}
async function dump(tag){console.log('=== '+tag+' ===');console.log('URL='+page.url());console.log('HEADINGS='+clean((await page.locator('h1,h2,h3').allTextContents().catch(()=>[])).join(' | ')));console.log('BODY='+clean(await page.locator('body').innerText().catch(()=> '')).slice(0,22000));const controls=await page.locator('input,textarea,select,button').evaluateAll(es=>es.slice(0,300).map((e,i)=>({i,tag:e.tagName,type:e.getAttribute('type'),id:e.id,name:e.getAttribute('name'),placeholder:e.getAttribute('placeholder'),value:('value'in e)?e.value:null,text:(e.textContent||'').trim().slice(0,700),checked:('checked'in e)?e.checked:null,options:e.tagName==='SELECT'?Array.from(e.options).map(o=>({t:(o.textContent||'').trim(),v:o.value,sel:o.selected})).slice(0,100):null}))).catch(()=>[]);for(const x of controls){if(x.type==='password')continue;console.log('CTRL '+JSON.stringify(x))}}
await login()
await page.goto('https://hq.ssrn.com/submission.cfm?submission-id=20260925-200912623',{waitUntil:'domcontentloaded',timeout:60000})
await cookies()
let body=clean(await page.locator('body').innerText().catch(()=>''))
console.log('OPEN='+clean((await page.locator('h1,h2,h3').allTextContents().catch(()=>[])).join(' | ')))
if(body.includes('Step 4: Classify Your Submission')){
  const selected=body.split('Previous Classifications')[0]
  if(!selected.includes('Global Commodity Issues Alert')){
    const choice=page.getByRole('button',{name:'Global Commodity Issues Alert',exact:true})
    if(await choice.isVisible().catch(()=>false)){await choice.click({force:true});await page.waitForTimeout(600)}
  }
  await save()
  await clickBtn(/Next Step/i)
  body=clean(await page.locator('body').innerText().catch(()=>''))
}
if(!body.includes('Step 5: Research Integrity'))throw new Error('Not on Step 5')
await page.locator('#declaration-of-interest').fill('This research was personally funded by the author. No external funding was received.')
await page.locator('#funder-statement').fill('This research was personally funded by the author. No external funding was received.')
const terms=page.locator('input[type="checkbox"][name*="I have reviewed each file"]').first()
if(!await terms.isVisible().catch(()=>false))throw new Error('Terms checkbox not found')
await terms.check({force:true})
await save()
await clickBtn(/Next Step/i)
await dump('STEP6')
const rights=page.locator('#license-option-6')
if(!await rights.isVisible().catch(()=>false))throw new Error('All-rights-reserved license option not found')
await rights.check({force:true})
await save()
await clickBtn(/Next Step/i)
await dump('STEP7')
await page.screenshot({path:'ssrn-step7.png',fullPage:true})
await browser.close()
