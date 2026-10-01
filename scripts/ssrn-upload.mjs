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

  if (process.env.SSRN_MODE === 'finalize') {
    const metadata = {
      '20260925-200912623': {
        title: 'The Physical Limits of Artificial Intelligence: Energy, Water, Critical Minerals and the Infrastructure Requirements of Advanced AI and Hypothetical Superintelligence, 2026-2035',
        date: '25/09/2026',
        abstract: 'Artificial intelligence is expanding within a physical system whose construction cycle is slower than the software economy. Data-centre capacity relies on power, grid connections, transformers, cooling, water, advanced chips, land, finance and social permission. This paper examines those physical bottlenecks, plausible development pathways, investment trade-offs and governance choices, while treating superintelligence as a contingent scenario rather than an established capability or forecast. It evaluates electricity, water, critical minerals, semiconductors, infrastructure, carbon accounting, cybersecurity and operational resilience as a coupled, location-specific industrial system. The analysis distinguishes domestic access to AI services from the more capital-intensive ambition to host frontier-model training, and proposes decision frameworks for boards and governments through 2035.',
        keywords: ['artificial intelligence','AI infrastructure','data centres','energy','water','critical minerals','semiconductors','superintelligence','governance'],
        classification: 'Environmental Economics Alert'
      },
      '20260930-150901833': {
        title: 'From Ore to Optionality: Why Critical-Mineral Partnerships Must Deliver Industrial Capability, Not Only Supply Security',
        date: '29/09/2026',
        abstract: 'This research monograph examines critical-mineral partnerships from the perspective of both supply security and productive transformation. Its central thesis is that partnership quality should be judged by the industrial options created, not only by tonnes moved. The paper compares producer and consumer economies, advanced and developing economies, and upstream and downstream policy approaches. It evaluates offtake, processing, technology, infrastructure, ownership pathways and network integration through the author’s OPTION framework, supported by a 48-indicator scorecard and 12-month implementation sequence. The analysis separates verified facts, projections, attributed institutional assessments and author propositions, and argues that resilient mineral partnerships should create dependable supply while building durable capabilities, linkages and economic optionality.',
        keywords: ['critical minerals','supply security','industrial policy','value addition','supply-chain resilience','mining','ESG','OPTION framework'],
        classification: 'Global Commodity Issues Alert'
      },
      '20260930-150923239': { classification: 'Environmental Economics Alert' },
      '20260930-190908378': { classification: 'Environmental, Social & Governance (ESG) Research Alert' },
      '20260930-190910213': { classification: 'Environmental, Social & Governance (ESG) Research Alert' },
      '20260930-190913144': { classification: 'International Finance Alert' },
      '20260930-190919009': { classification: 'Economic Growth Alert' },
      '20260930-190928409': { classification: 'New Institutional Economics Alert' },
      '20260930-190934140': { classification: 'New Institutional Economics Alert' }
    }

    const stepBody = async () => (await page.locator('body').innerText()).replace(/\s+/g, ' ')

    async function clickNext() {
      const next = await firstVisible(page.getByRole('button', { name: /^Next Step$/i }))
      if (!next) throw new Error('Next Step button not found on ' + page.url())
      await next.click({ force: true })
      await page.waitForTimeout(2600)
    }

    async function completeStep1(item) {
      const authorRadio = page.locator('#isAuthor')
      if (await authorRadio.count()) await authorRadio.check({ force: true }).catch(() => {})
      const combo = page.locator('#trigger-input-content-type')
      if (await combo.count()) {
        await combo.click({ force: true })
        await combo.fill('Preprint').catch(() => {})
        await page.waitForTimeout(700)
        const option = await firstVisible(page.getByText(/Preprint/i)).catch(() => null)
        if (option) await option.click({ force: true }).catch(() => {})
        else {
          await combo.press('ArrowDown').catch(() => {})
          await combo.press('Enter').catch(() => {})
        }
      }
      await clickNext()
    }

    async function completeStep2(item) {
      const m = metadata[item.submissionId] || {}
      const title = page.locator('#title')
      const abstract = page.locator('#abstract')
      if (m.title && await title.count()) {
        const current = (await title.innerText().catch(() => '')).trim()
        if (!current) await title.fill(m.title)
      }
      if (m.abstract && await abstract.count()) {
        const current = (await abstract.innerText().catch(() => '')).trim()
        if (!current) await abstract.fill(m.abstract)
      }
      const dateInput = page.getByLabel('Date paper was written')
      if (m.date && await dateInput.count()) {
        const current = await dateInput.inputValue().catch(() => '')
        if (!current) await dateInput.fill(m.date)
      }
      if (m.keywords?.length) {
        const kw = page.locator('#add-keyword')
        if (await kw.count()) {
          for (const word of m.keywords) {
            await kw.fill(word)
            await kw.press('Enter')
            await page.waitForTimeout(100)
          }
        }
      }
      await clickNext()
    }

    async function completeStep3(item) {
      const search = page.locator('#author-search')
      if (await search.count()) {
        await search.fill('Ragunauth Ramsaroop')
        await search.press('Enter')
        await page.waitForTimeout(1100)
        const authorName = await firstVisible(page.getByText('Ragunauth Ramsaroop', { exact: true }))
        if (!authorName) throw new Error('Author search result not found for ' + item.submissionId)
        await authorName.click({ force: true })
        await page.waitForTimeout(900)
      }
      await clickNext()
    }

    async function completeStep4(item) {
      const target = metadata[item.submissionId]?.classification
      if (!target) throw new Error('No classification mapping for ' + item.submissionId)
      let choice = await firstVisible(page.getByText(target, { exact: true })).catch(() => null)
      if (!choice) {
        const search = await firstVisible(page.locator('input[placeholder*="search" i], input[type="search"]')).catch(() => null)
        if (search) {
          await search.fill(target)
          await page.waitForTimeout(1200)
          choice = await firstVisible(page.getByText(target, { exact: true })).catch(() => null)
        }
      }
      if (!choice) throw new Error('Classification not found: ' + target + ' for ' + item.submissionId)
      await choice.click({ force: true })
      await page.waitForTimeout(700)
      await clickNext()
    }

    async function completeStep5() {
      const textareas = page.locator('textarea')
      const count = await textareas.count()
      if (count < 2) throw new Error('Research Integrity textareas not found')
      await textareas.nth(0).fill('No personal or financial conflicts of interest are disclosed in this manuscript. The author is an independent researcher and accepts full responsibility for the analysis, interpretations and conclusions.')
      await textareas.nth(1).fill('This research was personally funded by the author. No external funding was received.')
      if (count > 2) {
        await textareas.nth(2).fill('Not applicable. This research does not involve human participants, patients, personal health data, or clinical research.')
      }

      const rights = page.getByText(/I have reviewed each file that I am uploading and I have the right to upload this file\./i)
      const terms = page.getByText(/I have read and agree to the SSRN Terms and Conditions\./i)
      for (const labelText of [rights, terms]) {
        const label = await firstVisible(labelText).catch(() => null)
        if (label) {
          const parent = label.locator('xpath=..')
          const checkbox = parent.locator('input[type="checkbox"]')
          if (await checkbox.count()) await checkbox.first().check({ force: true }).catch(() => {})
          else await label.click({ force: true }).catch(() => {})
        }
      }

      const visibleChecks = page.locator('input[type="checkbox"]:visible')
      const n = await visibleChecks.count()
      for (let i=0; i<n; i++) {
        const cb = visibleChecks.nth(i)
        if (!(await cb.isChecked().catch(() => false))) await cb.check({ force: true }).catch(() => {})
      }
      await clickNext()
    }

    async function completeStep6() {
      let choice = await firstVisible(page.getByText(/All Rights Reserved/i)).catch(() => null)
      if (!choice) {
        const labels = page.locator('label')
        const n = await labels.count()
        for (let i=0;i<n;i++) {
          const label = labels.nth(i)
          if (/All Rights Reserved/i.test(await label.innerText().catch(() => ''))) {
            choice = label
            break
          }
        }
      }
      if (!choice) {
        console.log('SSRN_UNEXPECTED_LICENSE_PAGE=' + (await stepBody()).slice(0,6000))
        throw new Error('Expected All Rights Reserved licence option was not found')
      }
      await choice.click({ force: true })
      await page.waitForTimeout(500)
      await clickNext()
    }

    async function completeStep7(item) {
      const body = await stepBody()
      const unchecked = page.locator('input[type="checkbox"]:visible:not(:checked)')
      if (await unchecked.count()) {
        const labels = []
        for (let i=0;i<await unchecked.count();i++) {
          const cb = unchecked.nth(i)
          const id = await cb.getAttribute('id')
          let labelText = ''
          if (id) labelText = await page.locator(`label[for="${id}"]`).innerText().catch(() => '')
          labels.push(labelText)
        }
        const unknown = labels.filter(x => x && !/confirm|agree|submit|accuracy|author|rights/i.test(x))
        if (unknown.length) {
          console.log('SSRN_UNEXPECTED_FINAL_ATTESTATION=' + item.submissionId + ' :: ' + unknown.join(' | '))
          throw new Error('Unexpected final attestation requires review')
        }
        for (let i=0;i<await unchecked.count();i++) await unchecked.nth(i).check({ force: true }).catch(() => {})
      }

      const candidates = [
        page.getByRole('button', { name: /^Submit$/i }),
        page.getByRole('button', { name: /Submit Paper/i }),
        page.getByRole('button', { name: /Submit Submission/i })
      ]
      let submit = null
      for (const loc of candidates) {
        submit = await firstVisible(loc).catch(() => null)
        if (submit) break
      }
      if (!submit) {
        console.log('SSRN_REVIEW_PAGE=' + body.slice(0,7000))
        throw new Error('Final Submit button not found')
      }
      await submit.click({ force: true })
      await page.waitForTimeout(3500)
    }

    const finalResults = []
    for (const item of papers) {
      const rec = { submissionId: item.submissionId, status: 'started' }
      try {
        await page.goto(`https://hq.ssrn.com/submission.cfm?submission-id=${item.submissionId}`, {
          waitUntil: 'domcontentloaded',
          timeout: 60000
        })
        await dismissCookieOverlay(page)

        for (let pass=0; pass<10; pass++) {
          await page.waitForTimeout(900)
          const body = await stepBody()
          if (/Step 1:\s*Upload Submission/i.test(body)) await completeStep1(item)
          else if (/Step 2:\s*Confirm Key Submission Details/i.test(body)) await completeStep2(item)
          else if (/Step 3:\s*Author Information/i.test(body)) await completeStep3(item)
          else if (/Step 4:\s*Classify Your Submission/i.test(body)) await completeStep4(item)
          else if (/Step 5:\s*Research Integrity/i.test(body)) await completeStep5()
          else if (/Step 6:\s*Choose a license/i.test(body)) await completeStep6()
          else if (/Step 7:\s*Review and Submit/i.test(body)) {
            await completeStep7(item)
            break
          } else {
            break
          }
        }

        await page.goto('https://hq.ssrn.com/submissions/MyPapers.cfm', { waitUntil: 'domcontentloaded', timeout: 60000 })
        await dismissCookieOverlay(page)
        const dashboard = await stepBody()
        const draftStillVisible = dashboard.includes(item.submissionId) && /Draft/i.test(dashboard.slice(Math.max(0,dashboard.indexOf(item.submissionId)-500), dashboard.indexOf(item.submissionId)+1000))
        rec.status = draftStillVisible ? 'draft' : 'submitted'
        rec.dashboardExcerpt = dashboard.includes(item.submissionId)
          ? dashboard.slice(Math.max(0,dashboard.indexOf(item.submissionId)-250), dashboard.indexOf(item.submissionId)+750)
          : 'submission id not visible in current dashboard text'
      } catch (error) {
        rec.status = 'failed'
        rec.error = error instanceof Error ? error.message : String(error)
        rec.page = (await stepBody().catch(() => '')).slice(0,5000)
      }
      finalResults.push(rec)
      console.log('SSRN_FINAL=' + JSON.stringify(rec))
    }

    await fs.writeFile(path.join(outDir, 'final-results.json'), JSON.stringify(finalResults, null, 2))
    const failed = finalResults.filter(x => x.status === 'failed' || x.status === 'draft').length
    console.log('SSRN_FINAL_SUMMARY=' + JSON.stringify({submitted:finalResults.filter(x=>x.status==='submitted').length,remaining:failed}))
    if (failed) process.exitCode = 1
  }

  if (process.env.SSRN_MODE !== 'finalize') for (const item of papers) {
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
