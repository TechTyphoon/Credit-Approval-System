---
description:- Treat the PDF example typo `credit_limit`→`credit_rating` (interpret it as credit rating).

5) INTERNAL IMPLEMENTATION RULES (minimal)
- You may add only minimal internal technical fields (e.g., internal IDs, timestamps). **Do not** expose them in any API response unless PRD says so. If you add internal fields, prefix them with `_` and document why in `INTERNAL_FIELDS.md`.
- Background ingestion must use a worker. If you introduce a new dependency (e.g., Redis, Celery), document the reason succinctly in `DEPENDENCY_DECISION.md` and **get approval** before pushing.

6) DOCKER & RUNNING
- The final deliverable must run with a single `docker-compose up` as required by the PRD.
- Document exact run steps in `README.md` (human tone, minimal and clear). Sample run commands are allowed, but avoid robotic copy-paste sections.

7) QUALITY, TESTS, & SAFETY CHECKS (double-check, always)
Before committing and pushing any change, do this human-checked checklist:
- migrations created and applied locally (describe in one line if migrations are included),
- linter run and no new linter errors,
- basic unit tests run (if present) or smoke tests executed,
- `docker-compose up` launches (at least no immediate crash),
- one **manual** smoke test for each modified or new endpoint with example request/response recorded in the PR description.
Record the checklist result in the commit or PR description in 1–2 human sentences.

8) COMMITS & CHANGE DESCRIPTION (human)
- Each logical change = one commit.
- Commit subject: single human sentence (imperative or brief).
- Commit body: 1–2 short sentences explaining *why* the change was made (not the “how”).
- Pull request / change description must include: what was changed, why, how to test (short), and any open questions.

9) DOCUMENTATION: keep it human
- Update `README.md` with: how to run (docker-compose), how to trigger ingestion, and the exact list of API endpoints and request/response fields (as in PRD). Use short human examples (one example per endpoint). Avoid long templated READMEs.

10) EXAMPLES & SAMPLES
- When adding example requests/responses, present them clearly and with real-looking numbers. Use a minimal code fence for curl/json if necessary. Keep descriptions natural, not templated.

11) LOGS & DEBUG
- Remove debug prints and overly verbose logs before committing. Use proper logging with levels if needed.

12) IF YOU’RE TEMPTED TO DEVIATE
- Stop. Create `BLOCKED_BY_CLARIFICATION.md` and wait.

13) VOICE & STYLE (for docs, comments, commit messages)
- Human, direct, friendly. Short. No robotic phrasing. A little Gen-Z brevity is ok, but remain professional.
- Example: instead of "This endpoint returns a list of resources", write "Returns the customer's active loans. Example below."

---

ACKNOWLEDGEMENT RULE
- At the start of any session where you will modify files, create `ACTION_ACKNOWLEDGEMENT.md` with one line: `I will follow META.md rules. [ISO timestamp]` and a one-sentence note of what you will do in this session.

---

If you follow these rules, you will stay inside the PRD boundaries and deliver human-readable, high-quality work. If any rule conflicts with the PRD, the PRD wins — then create `BLOCKED_BY_CLARIFICATION.md` and ask Mahendra.

Do not change this file without Mahendra's explicit ok.
