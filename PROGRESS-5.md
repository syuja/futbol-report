# Job Search Progress Tracker

> Last updated: May 28, 2026 (~12:15 AM ET)
> Maintained as a working doc — update at the end of each session.

---

## Status Summary

| Milestone | Status |
|---|---|
| Personal site live with custom domain | ✅ Done |
| Real About page (bio + photo) | ✅ Done |
| Soccer bot mapped & documented | ✅ Done |
| Futbol-report repo + Python prototype running | ✅ Done |
| Multi-model pipeline (4 models via OpenRouter) | ✅ Done |
| First real eval run with comparative findings | ✅ Done |
| Persistence layer (Redis on Vercel) | ✅ Done |
| Comparison view on `samiryuja.dev` | ✅ Done |
| Run history selector | ✅ Done |
| Visitor voting | ✅ Done |
| Project linked in site Projects list | ✅ Done |
| Migration to Lambda + EventBridge | ✅ Done |
| Verify scheduled auto-runs (2–3 clean fires) | 🔄 In progress |
| Decommission harlie | ⏳ Blocked on verify |
| Telegram delivery from new system | ⏳ Not started |
| Project writeup page content | ⏳ Not started |
| Blog post writeup | ⏳ Not started |
| Hospitable Agent Phase 1 | ⏳ Not started |
| Airbnb coverage problem | ⏳ Not started |

---

## What Got Done

### Personal Site — `samiryuja.dev` (May 20, 26)

- Domain registered, GitHub repo, template forked (`tailwind-nextjs-starter-blog`), metadata updated
- Deployed to Vercel with custom domain + SSL
- Cleared template example content
- Replaced template placeholder author with real bio + photo on /about
- Husky pre-commit hook (lint-staged + Prettier) confirmed working — auto-formats before commit
- Site live at <https://samiryuja.dev> ✅

### Futbol Report — generator (May 20–21)

- Mapped existing harlie setup (cron → tmux → Claude Code → skill → Telegram MCP)
- Created `futbol-report` repo with `uv` (Python 3.12)
- Dependencies: `openai`, `requests`, `python-dotenv`, `redis`
- API keys in `.env` (gitignored): Brave Search, OpenRouter, Redis URL
- Ported skill markdown to `prompts/futbol_skill.md`; cleaned out dead Claude Code frontmatter
- Built `main.py`: Brave Search (`freshness=pw`, dated + competition-broadened queries incl. transfers/manager changes), anti-hallucination clause, multi-model loop, writes runs to Redis

### Futbol Report — website (May 25–26)

- Provisioned Redis on Vercel (free 30 MB tier, named `futbol-reports`)
- `lib/redis.ts` — `withRedis` helper + `getLatestRun`, `getRun`, `getAllTimestamps`, `getVotes`, `recordVote`
- `app/projects/futbol-report/page.tsx` — server-rendered comparison page, 2x2 grid, reads `?run=` param
- `RunSelector.tsx` (history dropdown), `VoteButton.tsx`, `app/api/vote/route.ts`
- Added `@/lib/*` path alias to `tsconfig.json`; linked project in `data/projectsData.ts`
- Live at <https://samiryuja.dev/projects/futbol-report> ✅

### Futbol Report — Lambda + EventBridge migration (May 27–28)

The generator now runs in the cloud on a schedule, not just on the laptop.

- `main.py` made Lambda-ready: added `run_pipeline()`, `handler(event, context)`, removed local file logging (CloudWatch captures stdout instead), `BASE_DIR` for the prompt path, and made the `dotenv` import optional via try/except so it works both locally and on Lambda
- `build_lambda.sh` — packaging script. Builds a Linux-targeted zip with `python3 -m pip --platform manylinux2014_x86_64 --only-binary=:all:`, pinning `pydantic-core==2.46.4` to force the correct Linux wheel
- Lambda function `futbol-report-generator` created: Python 3.12, x86_64, handler `main.handler`, timeout 900s, 512 MB, env vars set (Brave / OpenRouter / Redis)
- Deployed via AWS CLI (`aws lambda update-function-code`) after browser upload proved unreliable
- EventBridge Scheduler `futbol-report-schedule`: cron `0 8 */3 * ? *` in `America/New_York` (every 3 days at 8 AM ET), target = Lambda Invoke, auto-created execution role
- Manual test succeeded end to end: all 4 models ran, saved to Redis, new run appeared on the live site (~227s runtime)

### Hard-won lessons from the migration (interview-worthy war stories)

- **Runtime/binary mismatch:** Lambda was defaulted to Python 3.14 but the code was bundled for 3.12 — the `pydantic_core` C extension (a `cpython-312` `.so`) couldn't load. Fix: set the Lambda runtime to match the build target.
- **Mac vs. Linux binaries:** `uv`'s `--only-binary` didn't reliably fetch Linux wheels for `pydantic-core`; switching to `python3 -m pip` with explicit `--platform manylinux2014_x86_64` did.
- **Optional dependency:** `python-dotenv` isn't bundled for Lambda (env vars come from AWS), so the import had to be wrapped in try/except.
- **Timeout tuning:** default 3s → the pipeline needs ~4 min (13 Brave calls + 4 sequential model calls). Set to 900s ceiling.
- **Browser upload unreliable:** the console zip upload silently didn't update the deployed code (SHA-256 unchanged). AWS CLI upload was the reliable path.

### Models in current lineup

| Model | Slug | Notes |
|---|---|---|
| Claude Sonnet 4.5 | `anthropic/claude-sonnet-4.5` | Baseline |
| Kimi K2.6 | `moonshotai/kimi-k2.6` | Chinese open-weight MoE |
| Qwen 3.6 Flash | `qwen/qwen3.6-flash` | Small, fast, cheap |
| Gemma 4 31B IT | `google/gemma-4-31b-it` | Google open-weight, dense; cheapest |

---

## Architecture (current state)

```
EventBridge Scheduler  (cron: every 3 days, 8 AM ET)
        │  invokes
        ▼
AWS Lambda  (futbol-report-generator, Python 3.12)
  main.handler → Brave Search + OpenRouter (4 LLMs) → writes run to Redis
        │
        ▼
   Redis (Vercel, free tier)        ← shared handoff point
   - run:<timestamp>      = JSON {timestamp, generated_at, reports}
   - runs:index           = list of timestamps, newest first
   - votes:<ts>:<model>   = integer counter
        │
        ▼
samiryuja.dev/  (Next.js on Vercel)
  /projects/futbol-report  → server-renders the 2x2 comparison grid + history + voting
  /api/vote                → records votes

(Local: `uv run main.py` still works for manual runs / testing.)
(Old: harlie cron+tmux still running as fallback — retire after 2–3 clean scheduled fires.)
```

---

## Findings from Eval Runs

Real, observable, comparative findings — substance for the blog post and interview talking points.

1. **Brave search results are non-deterministic across runs.** Same query, ~30 min apart, different results. Not a bug (live re-ranking) but means context must be consistent within a run (it is — one Brave call feeds all 4 models) and the system must handle thin results gracefully.
2. **Anti-hallucination clause held across all 4 model families.** The "use ONLY facts present in search results" instruction generalized from Anthropic to Moonshot to Alibaba to Google. Prompt-level guardrails travel across model families.
3. **Models differ sharply on context filtering.** An out-of-scope Indian Super League match was filtered out by Claude/Qwen/Gemma but surfaced by Kimi. Same prompt, same data, different prioritization.
4. **Information utilization varies with model size/family.** Claude and Kimi used the most context; Qwen middle; Gemma (cheapest) compressed hardest. A real cost/quality tradeoff.
5. **Format adherence ranking:** Claude > Qwen > Kimi > Gemma.
6. **Manager-change and transfer queries materially improved off-season output.** When fixtures dried up after Serie A ended, these queries kept reports substantive (Allegri sacking, Guardiola departure). "Let the data lead" handled the seasonal pivot with no calendar logic.

---

## Known Issues / Future Improvements

### Secret scanning (NEW — do this soon)
Secrets leaked twice this session (Redis URL, then the full Lambda env-var block) by pasting command/console output, and had to be rotated each time. Add a pre-commit secret scanner — `gitleaks` or `trufflehog` — to both repos, ideally wired into the existing Husky pre-commit hook. Cheap insurance, and a good habit before AWS keys are involved. Also a genuine resume/interview point ("added secret scanning to the commit pipeline").

### Secrets handling hardening
API keys are currently Lambda environment variables — accepted and normal for this scale. The more rigorous tier is AWS Secrets Manager (encrypted, rotatable, audited). Not needed now; this is the answer to "how would you harden it?" in an interview.

### Voting integrity (deduplication)
Per-page-load only — a refresh lets the same person vote again. Rough signal, not a rigorous poll. Real fix needs cookies/localStorage/fingerprinting. Acceptable for v1.

### Report cell sizing / layout
Reports are different lengths, so the 2x2 grid reads as a 2-column stack. Later polish: cap cell height with internal scroll, or tabbed layout. Cosmetic.

### `main.py` still a flat file
Never refactored into modules — and that turned out fine; the Lambda migration didn't require it. Leave it until there's an actual reason (e.g. the file gets genuinely hard to navigate). Do NOT refactor ahead of need.

### Thin search runs
When Brave returns weak context, every model produces a sparse report. Fixes (both work with Brave): retry with broader queries, or fetch full page content for top results (Firecrawl / readability). Snippets are inherently lossy.

### `getVotes` uses Redis `KEYS`
Scans the whole keyspace. Fine at current scale. If it grows, switch to `SCAN` or a per-run hash.

### Page revalidation
Comparison page is `force-dynamic` (reads Redis every request). Works fine. ISR/scheduled revalidation is a later optimization only.

### Slow Lambda runtime (~4 min)
13 sequential Brave calls + 4 sequential model calls. Fine for a job that runs every 3 days. If ever bothersome: parallelize the Brave searches and/or the model calls. Not urgent.

### Projects page placeholder text
/projects still shows the template tagline "Showcase your projects with a hero image (16 x 9)". Swap for real copy. Lives in `app/projects/page.tsx`. Cosmetic, quick.

---

## Parked Ideas (deliberately NOT doing now)

Captured so they stop nagging. These are the tool-swap / scope-expansion pattern — revisit only with a concrete, job-search-relevant reason.

- **Build my own inference router (replace OpenRouter):** No. OpenRouter works and is a defensible choice. Building a router is weeks of work, un-ships a working system, and adds nothing to the job search. The interesting story is the *eval*, not the plumbing.
- **vast.ai serverless / different compute layer:** No. Lambda just started working tonight after a long slog. Don't swap the compute layer. Park indefinitely.
- **"More CI/CD for GitHub":** Undefined. Site already auto-deploys (Vercel) and has a pre-commit hook. Needs a specific goal before it's real work — the one concrete, worthwhile piece is the secret scanner above.

---

## What Remains (Project 0)

In priority order:

1. **Verify scheduled auto-runs.** First EventBridge fire is Thu May 28, 8 AM ET. Check the site dropdown for a new ~8 AM run you didn't trigger. Confirm 2–3 clean fires over the next ~week.
2. **Decommission harlie** — turn off its cron + tmux only after step 1 is confirmed. Until then it's the fallback.
3. **Telegram delivery from new system** — reuse the harlie bot token; send the "winning" report (by votes, or Claude's by default). Note: this can be added to the Lambda.
4. **Project writeup** on `/projects/futbol-report` — intro/explanation section above the grid (recruiter-facing; also blog raw material).
5. **Blog post:** "Building a serverless multi-model report engine with live voting eval." The migration war stories above are great material.
6. **Optional polish:** secret scanner, full-page-content fetching, vote dedup, cell sizing, projects-page copy.

---

## Resume Material

### Truthfully claimable today

- Deployed a Next.js + Vercel portfolio with custom domain, automated CI/CD, and SSL
- Built and deployed an **event-driven serverless system on AWS** (Lambda + EventBridge Scheduler) that runs a scheduled multi-model LLM evaluation pipeline, integrating Brave Search and four frontier models (Anthropic Claude, Moonshot Kimi K2.6, Alibaba Qwen, Google Gemma) via OpenRouter, persisting results to Redis and rendering them on a public site with run history and visitor voting
- Diagnosed and resolved real serverless deployment issues: Python runtime/native-binary mismatches, Linux wheel packaging for `pydantic-core`, optional-dependency handling, and Lambda timeout tuning
- Surfaced measurable differences across model families in format adherence, context filtering, and information density on a repeated task; identified upstream search-API non-determinism and designed around it
- Made and can defend concrete architecture decisions: server-rendered vs. client-fetched pages, key-value vs. object storage, inference broker vs. direct provider SDKs, env vars vs. Secrets Manager

### What to NOT say

- Do not undersell this. "I just call APIs" is the inversion of "I built and shipped a live, scheduled, serverless multi-model eval framework end to end — ingestion, multi-provider inference, persistence, a public web UI with voting, running automatically on AWS — and debugged the real deployment failures along the way."

---

## When You Sit Back Down

Project 0's infrastructure is **done and automated**. The pipeline runs itself on AWS every 3 days.

Immediate, low-effort next step: **confirm the scheduled run fired.** After Thu May 28 ~8 AM ET, open the site dropdown and look for a run you didn't trigger. That's the proof the automation works.

Then the highest-value remaining work is **making the project legible to other people**, not more infrastructure:

1. Write the project intro section on `/projects/futbol-report` (recruiter-facing, quick, doubles as blog material).
2. Draft the blog post — the migration war stories in this doc are the raw material.
3. Add the secret scanner (real, quick, good habit + resume point).

Only after 2–3 clean scheduled runs: retire harlie.

Bigger picture: Project 0 is essentially complete. The next *project* in the strategy doc (Hospitable Agent / Airbnb work) is where to point energy once the writeup and harlie cleanup are done — that's new résumé surface area, whereas more polish on Project 0 has diminishing returns.

---

## Anti-Distraction Reminders

From the strategy doc, Section 13:

1. One project at a time, shipped with public artifacts, beats eleven unfinished ones.
2. The AI familiarity gap is real but temporary — closes with project work, not study.
3. Underselling specific resume bullets and skills will cost interviews more than any missing technical skill.

Patterns observed across these sessions:

- Tool-swap research (Tavily, Cloudflare, templates, Brave, smaller Kimi models, and now "build my own router" / "vast.ai") is avoidance in disguise. Decide, move. The Parked Ideas section exists to hold these so they stop pulling focus.
- Scope expansion mid-build ("set up email", "World Cup pivot now") is the same pattern.
- Tidying/refactoring right after a milestone instead of pushing forward is a subtler version.
- You shipped a complete, live, automated, multi-part system across these sessions — including pushing through a genuinely frustrating AWS deployment slog tonight. That persistence is the thing that matters. Keep going.
