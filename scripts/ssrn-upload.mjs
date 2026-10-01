import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { chromium } from 'playwright'

const EMAIL = process.env.SSRN_EMAIL
const PASSWORD = process.env.SSRN_PASSWORD

if (!EMAIL || !PASSWORD) {
  throw new Error('Missing SSRN_EMAIL or SSRN_PASSWORD environment variable')
}

const BASE_ASSET = 'https://d0ed54fb-3316-41e7-8a1f-a05ef6e61615.sandbox.floot.app'

const papers = [
  {
    submissionId: '20260925-200912623',
    name: 'SSRN_READY_The_Physical_Limits_of_Artificial_Intelligence.pdf',
    url: BASE_ASSET + '/_cdn/static/b4f42504-bb34-44a1-b9c7-695a07d298f8-SSRN_READY_The_Physical_Limits_of_Artificial_Intelligence.pdf'
  },
  {
    submissionId: '20260930-150901833',
    name: 'SSRN_READY_From_Ore_to_Optionality.pdf',
    url: BASE_ASSET + '/_cdn/static/9c44ac8e-ebdd-456a-829b-4d3f841a8b64-SSRN_READY_From_Ore_to_Optionality.pdf'
  },
  {
    submissionId: '20260930-150923239',
    name: 'SSRN_READY_Fresh_Water_The_Next_Strategic_Commodity.pdf',
    url: BASE_ASSET + '/_cdn/static/13b297c8-682f-4bfd-b6fc-ebd6cf967030-SSRN_READY_Fresh_Water_The_Next_Strategic_Commodity.pdf'
  },
  {
    submissionId: '20260930-190908378',
    name: 'SSRN_READY_Beyond_Employment.pdf',
    url: BASE_ASSET + '/_cdn/static/2fc7d82c-1fb3-4f3b-9b5c-97dcfa1c22b0-SSRN_READY_Beyond_Employment.pdf'
  },
  {
    submissionId: '20260930-190910213',
    name: 'SSRN_READY_Karpowership_Guyana_2035.pdf',
    url: BASE_ASSET + '/_cdn/static/2666c7fc-ef4e-4a90-a1e1-6508785a95bf-SSRN_READY_Karpowership_Guyana_2035.pdf'
  },
  {
    submissionId: '20260930-190913144',
    name: 'SSRN_READY_The_Geopolitics_of_Gold.pdf',
    url: BASE_ASSET + '/_cdn/static/c8cd1271-378b-4cbe-b9bd-8d56c5c0e94a-SSRN_READY_The_Geopolitics_of_Gold.pdf'
  },
  {
    submissionId: '20260930-190919009',
    name: 'SSRN_READY_Guyana_Development_Bank.pdf',
    url: BASE_ASSET + '/_cdn/static/57754df9-e613-4f12-9812-e6e461563365-SSRN_READY_Guyana_Development_Bank.pdf'
  },
  {
    submissionId: '20260930-190928409',
    name: 'SSRN_READY_Sovereign_AI.pdf',
    url: BASE_ASSET + '/_cdn/static/8282db85-9a13-4b60-9bef-0e5474223625-SSRN_READY_Sovereign_AI.pdf'
  },
  {
    submissionId: '20260930-190934140',
    name: 'SSRN_READY_The_Trust_Deficit.pdf',
    url: BASE_ASSET + '/_cdn/static/02900745-78bd-4347-92bd-d0fd865cc6d5-SSRN_READY_The_Trust_Deficit.pdf'
  }
]

const outDir = path.resolve('ssrn-run')
const downloadsDir = path.join(outDir, 'downloads')
await fs.mkdir(downloadsDir, { recursive: true })

async function downloadPdf(item) {
  const target = path.join(downloadsDir, item.name)
  const response = await fetch(item.url, {
    headers: { 'User-Agent': 'Mozilla/5.0' }
  })
  if (!response.ok) throw new Error(`Download failed for ${item.name}: HTTP ${response.status}`)
  const bytes = Buffer.from(await response.arrayBuffer())
  if (bytes.length < 5 || bytes.subarray(0, 5).toString() !== '%PDF-') {
    throw new Error(`Downloaded asset is not a PDF: ${item.name}`)
  }
  await fs.writeFile(target, bytes)
  return target
}

async function firstVisible(locator) {
  const count = await locator.count()
  for (let i = 0; i < count; i += 1) {
    const candidate = locator.nth(i)
    if (await candidate.isVisible().catch(() => false)) return candidate
  }
  return null
}

async function dismissCookieOverlay(page) {
  const selectors = [
    '#onetrust-accept-btn-handler',
    '#onetrust-reject-all-handler',
    '.onetrust-close-btn-handler',
    'button[aria-label*="Close" i]'
  ]
  for (const selector of selectors) {
    const button = await firstVisible(page.locator(selector)).catch(() => null)
    if (button) {
      await button.click({ force: true }).catch(() => {})
      await page.waitForTimeout(300)
    }
  }
  await page.evaluate(() => {
    const sdk = document.querySelector('#onetrust-consent-sdk')
    if (sdk) sdk.remove()
    document.documentElement.style.overflow = ''
    document.body.style.overflow = ''
  }).catch(() => {})
}

async function signIn(page) {
  await page.goto('https://hq.ssrn.com/submissions/MyPapers.cfm', { waitUntil: 'domcontentloaded', timeout: 60000 })
  await dismissCookieOverlay(page)

  const password = await firstVisible(page.locator('input[type="password"]'))
  if (!password) {
    if (/MyPapers\.cfm/i.test(page.url())) return
    throw new Error(`Unexpected SSRN page before login: ${page.url()}`)
  }

  const emailSelectors = [
    'input[placeholder*="Email" i]',
    'input[type="email"]',
    'input[name*="email" i]',
    'input[id*="email" i]',
    'input[name*="user" i]',
    'input[id*="user" i]'
  ]
  for (const selector of emailSelectors) {
    const email = await firstVisible(page.locator(selector))
    if (email) {
      await email.fill(EMAIL)
      break
    }
  }

  await password.fill(PASSWORD)

  let signInButton = await firstVisible(page.getByRole('button', { name: /sign in/i }))
  if (!signInButton) {
    signInButton = await firstVisible(page.locator('input[type="submit"][value*="sign" i]'))
  }
  if (!signInButton) throw new Error('SSRN Sign in button was not found')

  await dismissCookieOverlay(page)
  await Promise.all([
    page.waitForLoadState('domcontentloaded').catch(() => {}),
    signInButton.click({ force: true })
  ])

  await page.waitForTimeout(2000)

  if (await firstVisible(page.locator('input[type="password"]'))) {
    const bodyText = await page.locator('body').innerText().catch(() => '')
    console.log('SSRN_LOGIN_URL=' + page.url())
    console.log('SSRN_LOGIN_TITLE=' + await page.title().catch(() => ''))
    console.log('SSRN_LOGIN_TEXT=' + bodyText.slice(0, 5000).replace(/\n/g, ' | '))
    await page.screenshot({ path: path.join(outDir, 'login-failed.png'), fullPage: true }).catch(() => {})
    throw new Error('SSRN login did not complete. Check credentials or any SSRN verification prompt.')
  }
}

async function selectPreprint(page) {
  const selects = page.locator('select')
  const count = await selects.count()
  for (let i = 0; i < count; i += 1) {
    const select = selects.nth(i)
    const options = await select.locator('option').allTextContents().catch(() => [])
    const index = options.findIndex(x => /preprint/i.test(x))
    if (index >= 0) {
      const option = select.locator('option').nth(index)
      const value = await option.getAttribute('value')
      if (value !== null) {
        await select.selectOption(value)
        return true
      }
    }
  }
  return false
}

async function ensureAuthorSelected(page) {
  const byLabel = page.getByLabel(/I am the Author/i)
  if (await byLabel.count()) {
    const control = byLabel.first()
    if (await control.isVisible().catch(() => false)) {
      await control.check().catch(() => {})
      return
    }
  }

  const labels = page.locator('label')
  const count = await labels.count()
  for (let i = 0; i < count; i += 1) {
    const label = labels.nth(i)
    const text = (await label.innerText().catch(() => '')).trim()
    if (/I am the Author/i.test(text)) {
      await label.click().catch(() => {})
      return
    }
  }
}

async function clickSave(page) {
  const candidates = [
    page.getByRole('button', { name: /save and next step/i }),
    page.getByRole('button', { name: /^save$/i }),
    page.locator('input[type="submit"][value*="Save" i]')
  ]

  for (const locator of candidates) {
    const button = await firstVisible(locator)
    if (button) {
      await Promise.all([
        page.waitForLoadState('domcontentloaded').catch(() => {}),
        button.click()
      ])
      return
    }
  }
  throw new Error('No visible SSRN Save button found')
}

const browser = await chromium.launch({
  headless: true,
  args: ['--disable-blink-features=AutomationControlled']
})

const context = await browser.newContext({
  viewport: { width: 1440, height: 1100 },
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36'
})

const page = await context.newPage()
page.setDefaultTimeout(30000)

const results = []

try {
  await signIn(page)

  if (process.env.SSRN_MODE === 'inspect') {
    const item = papers[1]
    await page.goto(`https://hq.ssrn.com/submission.cfm?submission-id=${item.submissionId}`, {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    })
    await dismissCookieOverlay(page)
    await page.waitForTimeout(3500)
    const opener = await firstVisible(page.getByText('Select an Item', { exact: true })).catch(() => null)
    if (opener) await opener.click({ force: true }).catch(() => {})
    await page.waitForTimeout(700)
    console.log('SSRN_OPTIONS_TEXT=' + (await page.locator('body').innerText()).replace(/\s+/g,' ').slice(0,12000))
    const roles = await page.locator('[role="combobox"],[role="option"],[role="listbox"],button,input:not([type="password"])').evaluateAll(nodes => nodes.map(n => ({
      tag:n.tagName, role:n.getAttribute('role')||'', type:n.getAttribute('type')||'', name:n.getAttribute('name')||'',
      id:n.id||'', text:(n.innerText||n.value||'').trim(), aria:n.getAttribute('aria-label')||'',
      expanded:n.getAttribute('aria-expanded')||'', controls:n.getAttribute('aria-controls')||'', cls:n.className||''
    }))).catch(() => [])
    console.log('SSRN_OPTION_NODES=' + JSON.stringify(roles))
    process.exit(0)
  }

  for (const item of papers) {
    const record = {
      submissionId: item.submissionId,
      file: item.name,
      status: 'started'
    }

    try {
      const pdfPath = await downloadPdf(item)
      record.bytes = (await fs.stat(pdfPath)).size

      await page.goto(`https://hq.ssrn.com/submission.cfm?submission-id=${item.submissionId}`, {
        waitUntil: 'domcontentloaded',
        timeout: 60000
      })

      if (await firstVisible(page.locator('input[type="password"]'))) {
        await signIn(page)
        await page.goto(`https://hq.ssrn.com/submission.cfm?submission-id=${item.submissionId}`, {
          waitUntil: 'domcontentloaded',
          timeout: 60000
        })
      }

      await dismissCookieOverlay(page)
      const fileInput = page.locator('input[type="file"]').first()
      await fileInput.waitFor({ state: 'attached', timeout: 30000 })

      await ensureAuthorSelected(page)
      record.preprintSelected = await selectPreprint(page)

      await fileInput.setInputFiles(pdfPath)
      await page.waitForTimeout(2500)

      const attachedNameVisible =
        await page.getByText(item.name, { exact: false }).count().catch(() => 0)

      record.filenameVisibleBeforeSave = attachedNameVisible > 0

      await clickSave(page)
      await page.waitForTimeout(2500)

      if (await firstVisible(page.locator('input[type="password"]'))) {
        throw new Error('SSRN session expired while saving the draft')
      }

      record.status = 'uploaded'
      record.afterSaveUrl = page.url()
      await page.screenshot({
        path: path.join(outDir, `${item.submissionId}-uploaded.png`),
        fullPage: true
      }).catch(() => {})
    } catch (error) {
      record.status = 'failed'
      record.error = error instanceof Error ? error.message : String(error)
      await page.screenshot({
        path: path.join(outDir, `${item.submissionId}-failed.png`),
        fullPage: true
      }).catch(() => {})
    }

    results.push(record)
    console.log(JSON.stringify(record))
  }
} finally {
  await fs.writeFile(path.join(outDir, 'results.json'), JSON.stringify(results, null, 2))
  await browser.close()
}

const uploaded = results.filter(x => x.status === 'uploaded').length
const failed = results.filter(x => x.status === 'failed').length

console.log(`SSRN upload run complete: ${uploaded} uploaded, ${failed} failed`)

if (failed > 0) process.exitCode = 1
