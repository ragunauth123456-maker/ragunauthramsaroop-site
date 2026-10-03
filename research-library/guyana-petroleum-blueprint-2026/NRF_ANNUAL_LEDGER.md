# NRF ANNUAL STOCK-FLOW LEDGER
## 2020 through H1 2026

This workbook separates opening stock, petroleum inflows, investment return, lawful withdrawals and closing stock. It is designed to prevent common errors such as mixing cash with accruals, adding a forecast to an observed balance, or treating a withdrawal as a loss.

### Accounting identity

Opening balance + petroleum/other inflows + investment result - withdrawals = closing balance, subject to currency translation, receivable timing and other disclosed accounting adjustments.

### Current reconciliation status

- 2022-2025 are substantially reconciled to official Bank of Guyana year-end reporting.
- 2020-2021 preserve provisional annual bridges pending a direct line-by-line extraction of the audited annual statements.
- H1 2026 is partial-year evidence and is not treated as an audited full-year row.
- The machine-readable companion is `NRF_ANNUAL_LEDGER.csv`.
- Currency values in the CSV are USD millions and rounded. Underlying GYD values and source statements control where rounding produces small residuals.

### Audit rules

1. Cash receipt date, accrual-recognition date and cargo-lifting date are different fields.
2. Profit oil, royalty, signature bonus, investment return and withdrawal are separate categories.
3. A government projection is never inserted as an observed inflow.
4. A transfer to the Consolidated Fund is a withdrawal from the NRF, not evidence that a public project has been completed.
5. Any derived value is labelled derived and should be replaced by a direct primary-source figure when available.
6. The final edition must pin every row to the exact audited or quarterly report page/table.

### Key observations

The ledger demonstrates why a sovereign-fund narrative cannot be reduced to the closing balance. During 2022-2025, large petroleum inflows occurred at the same time as increasingly large lawful transfers to the Consolidated Fund. The balance therefore reflects at least three moving components: new petroleum receipts, investment income and withdrawals.

The 2025 row is particularly instructive. Official reporting records approximately US$2.51 billion of inflows and US$142.13 million of investment income, while approximately US$2.463 billion was transferred out. The year-end balance still increased relative to 2024 because inflows plus investment income exceeded withdrawals. [S88, S109]

The H1 2026 row should remain visibly different. It is a half-year observation from government reporting, not a substitute for audited 2026 annual accounts. [S07, S96]


## Edition 2.0 exception investigation: the 2025 receivable and H1 2026 recognition bridge

The original draft put the government's reported **US$1,997 million** of first-half 2026 profit-oil proceeds and royalties into a single stock-flow equation with the Bank of Guyana's **2025 year-end accrual NAV**. That is not a consistent accounting boundary. It produced a spurious discrepancy that should not have been marked as reconciled. [S07, S88, S134]

### Exhibit: why the balance bases differ

| Measured quantity | Value (US$ million, approximate) | Treatment |
|---|---:|---|
| December 2025 cash-basis closing balance | 3,250.41 | Bank of Guyana December cash-basis monthly statement. [S137] |
| Receivables reported at 2025 year-end | 184.11 | GYD 38,387,708 thousand at GYD 208.5/US$ from Q1 2026 comparative financial position. [S134] |
| December 2025 audited NAV, cash plus receivables | 3,434.53 | Audited IFRS closing balance / Q1 comparative. [S88, S134] |
| Ministry-reported H1 2026 profit-oil and royalty cash receipts | 1,997.00 | US$1,778.6m profit oil plus US$218.4m royalty. [S07] |
| H1 2026 investment income reported by government | 66.90 | Partial-year observation. [S07] |
| H1 2026 Consolidated Fund withdrawals | 1,020.00 | Partial-year observation. [S07] |
| Bank of Guyana/Ministry end-June 2026 fund balance | 4,294.20 | H1 closing stock. [S07, S136] |

The arithmetic is transparent:

1. If one starts from 2025 **accrual** NAV, the implied H1 fund inflows before investment income are 4,294.20 - 3,434.53 + 1,020.00 - 66.90 = **US$1,812.77m**, conditional on no other valuation/reclassification items.
2. The government-reported H1 **cash receipts** are US$1,997.00m. The gap relative to that implied figure is **US$184.23m**.
3. The year-end 2025 receivable is GYD 38.387708bn / 208.5 = about **US$184.11m**. The gap therefore very closely matches the amount recognized as a 2025 receivable.
4. The 2026 mid-year report says H1 profit-oil cash receipts include payments for **three lifts made in Q4 2025**. This supports a prior-year accrual/2026 settlement explanation, but is not a transaction-level reconciliation on its own. [S07, S134, S137]

The approximately **US$0.12m** difference between the rounded apparent gap and the translated receivable must not be concealed. It may reflect rounding, currency conventions, other cash/accrual timing or reporting differences. Those possibilities are hypotheses, not established adjustments. An audit-grade final reconciliation needs exact GYD entries, BoG Q2 2026 report figures and the dates/amounts for each of the three Q4 2025 lift settlements.

### Required cargo-to-cash audit procedure

Create one line for each government entitlement cargo with production period, cargo lifting date, invoice/settlement value, year-end receivable recognition, cash receipt date, NRF bank posting, government receipt notification and reported year. Tie the sum of 2025 receivables paid in 2026 to a reduction in receivables on the fund's financial position and to the corresponding 2026 cash statement. Only then classify the bridge as verified.

The treatment affects more than this one table. It determines whether a chart correctly attributes petroleum revenue to 2025 or 2026; whether a withdrawal-to-inflow ratio compares like periods; and whether a rapid rise in reported cash receipts is mistaken for wholly new production-derived revenue.

**Editorial disposition:** The 2026-H1 row is **open**, not reconciled. The 2025 receivable is a strong candidate explaining the difference, supported by primary financial statements and the Ministry's account of delayed Q4 lifts, but the precise transaction bridge and minor residual are outstanding. This distinction should remain in every PDF chart and executive summary.
