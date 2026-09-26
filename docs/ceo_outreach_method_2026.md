# Evidence-led CEO outreach | 2026

The private outreach cohort uses the top 200 companies in the 2026 Fortune Global 500 by revenue. Published 28 July 2026. The list defines the research cohort, not a commitment to send 200 unsuitable or unverified messages.

Source: https://fortune.com/ranking/global500/

## Company-by-company requirements

1. Verify the current CEO from an official leadership page.
2. Document a dated primary source for a strategic company priority.
3. Write the Minto thesis first. Add two to four business-specific supporting reasons, followed by approved CV evidence.
4. Build a restrained two- or three-page company-inspired CV, plus a one-page proposal with clickable primary-source links. Never use a company logo or imply employment or endorsement.
5. Use a verified publicly listed work contact or a clearly identified corporate or country office. Request forwarding when the address is not the CEO's verified professional email. No guessed personal addresses or misdirected investor, press or whistleblower mail.
6. Search the private sent ledger for duplicates before contacting any company. Check the sender, both attachments, and evidence sources.
7. Send through the authorized Gmail connection. Use the verified iCloud sending identity where available. Record actual SENT confirmation and Gmail message ID privately.
8. Review replies and bounces before sending one relevant follow-up. Stop on opt-out.

The script ../scripts/ceo_outreach_gate.py applies an offline quality gate to a private JSON array of dossiers. It does not send emails, scrape contact information, run on a timer, or publish the private campaign.

Example local invocation:

    python scripts/ceo_outreach_gate.py C:\private\ceo-dossiers.json --files-root C:\private\executive-pdfs --sent-ledger C:\private\sent-ledger.json

Each dossier provides: company, ceo, fortune_2026_rank, ceo_source_url, strategy_sources (url and published_at), value_thesis, supporting_reasons (2-4), approved_cv_evidence, contact_route (address, type, source_url, direct_verified), subject, message, attachments (cv_pdf and value_brief_pdf), and status.

Privacy boundary: the live tracker, recipient lists, tailored personal CVs, reply records and Gmail IDs stay outside this public GitHub Pages repository. Lundin Mining and Ivanhoe Mines are earlier pilot introductions, separate from the 2026 Fortune top-200 cohort.
