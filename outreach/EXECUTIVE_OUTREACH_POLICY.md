# Executive Outreach Policy

Policy version: executive-whitepaper-v1

## Executive-company outreach

Executive-company outreach is not a conventional resume submission.

Every message to a company executive must be addressed to a named senior decision-maker using a verified individual business email. Generic or functional mailboxes do not count as executive coverage and are blocked for this campaign type.

Blocked examples include press, media, communications, public relations, investor relations, careers, talent, recruiting, recruitment, HR, info, contact, support, sales, general office mailboxes, and shared aliases such as ceo@ or president@.

Acceptable recipients include CEO or President, Country Managing Director or Country President, C-suite executives, EVP/SVP, VP or Head of Corporate Affairs, External Affairs, Government Affairs, Public Policy, Sustainability, Stakeholder Relations, or senior People leadership when directly relevant to the opportunity.

Do not guess an individual's email pattern. The payload must state that the professional email was verified and record the verification source. The recipient's current senior role must also have a source URL.

## Required executive attachment

The primary attachment for `campaign_type: executive_company` is a bespoke Strategic Value Creation Brief prepared specifically for that company and recipient.

The brief must contain:

1. Executive brief
2. Company strategic context
3. Three to five company-specific strategic opportunities
4. A clear explanation of where Ragunauth Ramsaroop can add value
5. A 90-180 day action framework
6. Potential business impact
7. Why the background is relevant
8. At least three dated research sources
9. The executive CV appended as the final three pages

The paper must be based on genuine company research. Replacing only the company name in a generic template is not sufficient.

## Recruiter outreach

`campaign_type: recruiter` remains CV-first. A named recruiter at a legitimate recruiting or executive-search firm is a valid recipient. Generic talent or careers inboxes should still be avoided when a named recruiter is available.

## ATS and formal applications

`campaign_type: ats_application` remains ATS-first. Use the ATS executive CV and a role-specific cover letter when appropriate. Do not replace an ATS resume with the strategic white paper where a portal is designed to parse resumes.

## Duplicate and coverage rule

Before every executive send, check prior campaign records and Sent history. Do not send again to the same named executive unless the user explicitly approves a follow-up.

A company contacted only through a generic or functional mailbox is not considered covered. Its status remains `generic-only, executive unresolved` until a legitimate named senior decision-maker has been contacted successfully.

## Send gate

New untyped company outreach is blocked. Each payload must declare one of:

- `executive_company`
- `recruiter`
- `ats_application`

For `executive_company`, the GitHub workflow must run `scripts/prepare_outreach_payload.py` before SMTP transmission. The preflight validates the recipient, validates the research brief, generates the combined strategic-paper-plus-CV PDF, and injects that generated attachment into the approved payload.
