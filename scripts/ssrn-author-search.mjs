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
async function cookies(){const a=page.locator('#onetrust-accept-btn-handler');await a.waitFor({state:'visible',timeout:7000}).catch(()=>{});if(await a.isVisible().catch(()=>false)){await a.click({force:true});await page.waitForTimeout(700)}}
async function login(){await page.goto('https://hq.ssrn.com/submissions/MyPapers.cfm',{waitUntil:'domcontentloaded',timeout:60000});await cookies();const pw=await firstVisible(page.locator('input[type="password"]'));if(!pw)return;const em=await firstVisible(page.locator('input[name="input-email"],input[placeholder*="Email" i],input[type="email"]'));if(!em)throw new Error('No email field');await em.fill(EMAIL);await pw.fill(PASSWORD);await cookies();let b=await firstVisible(page.locator('#signinBtn'));if(!b)b=await firstVisible(page.getByRole('button',{name:/sign in/i}));if(!b)throw new Error('No sign in button');await b.click();await page.waitForTimeout(5000);if(await firstVisible(page.locator('input[type="password"]')))throw new Error('Login failed')}
async function clickButton(name){const b=await firstVisible(page.getByRole('button',{name}));if(!b)throw new Error('Button not found: '+name);await b.click({force:true});await page.waitForTimeout(1300)}
async function closeSaveNotice(){await page.keyboard.press('Escape').catch(()=>{});const d=page.locator('[role="dialog"]');if(await d.isVisible().catch(()=>false)){const x=await firstVisible(d.locator('button'));if(x)await x.click({force:true}).catch(()=>{})}await page.waitForTimeout(300)}
function clean(s){return String(s??'').replace(/\s+/g,' ').trim()}

await login()
await page.goto('https://hq.ssrn.com/submission.cfm?submission-id=20260925-200912623',{waitUntil:'domcontentloaded',timeout:60000})
await cookies()

let body=clean(await page.locator('body').innerText().catch(()=>''))
console.log('OPEN_HEADINGS='+clean((await page.locator('h1,h2,h3').allTextContents()).join(' | ')))

if(body.includes('Step 2: Confirm Key Submission Details')){
  const date=page.locator('input[placeholder="dd/mm/yyyy"]').first()
  if(await date.isVisible().catch(()=>false) && !await date.inputValue().catch(()=>'')) await date.fill('25/09/2026')
  await clickButton(/^Save$/i)
  console.log('STEP2_SAVE_TEXT='+clean(await page.locator('body').innerText().catch(()=>'')).slice(0,2500))
  await closeSaveNotice()
  await clickButton(/Next Step/i)
}

body=clean(await page.locator('body').innerText().catch(()=>''))
console.log('AFTER_ADVANCE_HEADINGS='+clean((await page.locator('h1,h2,h3').allTextContents()).join(' | ')))
if(!body.includes('Step 3: Author Information')) throw new Error('Did not reach Author Information')

const search=page.locator('#author-search')
await search.fill(EMAIL)
await search.press('Enter')
await page.waitForTimeout(1800)
console.log('AUTHOR_RESULTS_BODY='+clean(await page.locator('body').innerText().catch(()=>'')).slice(0,7000))
const candidates=await page.locator('button,a,[role="option"],[role="listitem"],li').evaluateAll(es=>es.map((e,i)=>({i,tag:e.tagName,text:(e.textContent||'').replace(/\s+/g,' ').trim().slice(0,500),id:e.id,class:e.className,role:e.getAttribute('role')})).filter(x=>x.text).slice(0,180))
console.log('AUTHOR_CANDIDATES='+JSON.stringify(candidates))
await page.screenshot({path:'ssrn-author-search.png',fullPage:true})
await browser.close()
