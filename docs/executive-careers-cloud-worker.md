# Executive careers public-source cloud worker

This read-only GitHub Actions worker runs offline QA on pull requests and checks three official, public employer careers pages daily after the workflow merges to the repository default branch. The initial source list covers Cardinal Health, Caterpillar and Bayer. Review and extend only with confirmed official employer career URLs.

The output artifact is `executive-careers-artifacts/public_research.json` and contains links **possibly** matching senior ESG, corporate affairs, sustainability, government relations and related roles. A link alone is not evidence of a live position, eligibility, visa sponsorship or company interest. JavaScript-only pages and rate-limited sites may produce no links. The workflow reports inaccessible sources rather than inventing job openings.

The worker **does not access Gmail, AgentMail, private CVs, recruiter contact data, secrets, or user-owned computers. It does not send messages, schedule emails, submit applications or accept site privacy terms.** No GitHub workflow may be used to retry or circumvent blocked outbound requests. Any later candidate-specific dossier must be private and pass the existing `scripts/ceo_outreach_gate.py` checks with current status, suppression and company-level dedup reviewed by a human.

To trigger the public research worker, use the workflow's manual Run workflow control after merge. For QA before merge, open the pull request and review the `qa` job. All source links and opportunity hypotheses need manual confirmation against the employer's current posting and immigration requirements. No recruitment performance, response, delivery, or interviews are claimed by these tests.
