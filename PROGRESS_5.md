# Job Search Progress Tracker

> Last updated: May 31, 2026
> Project 0 wrap-up day. Infrastructure complete. Remaining work is publication + a few polish items.

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
| First scheduled auto-run confirmed | ✅ Done |
| Redis index hygiene (prune + cap + TTLs) | ✅ Done |
| Project writeup page (intro + how-it-works + diagram + repo links) | ✅ Done |
| Harlie decommissioned | ✅ Done |
| CI security scanning (gitleaks + OSV) on both repos | ⏳ Today |
| Vote deduplication | ⏳ Today |
| Telegram delivery from Lambda | ⏳ Today |
| Projects-page placeholder copy swap | ⏳ Today (small) |
| Blog post writeup | ⏳ Today (highest leverage) |
| Hospitable Agent Phase 1 | ⏳ Project 1 (next) |
| Airbnb coverage problem | ⏳ Project 1 (next) |

---

## What Got Done

### Personal Site — `samiryuja.dev` (May 20, May 26)

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

- Provisioned Redis on Vercel (30 MB hobby tier, named `futbol-reports`, eviction policy `volatile-lru`)
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
- Deployed via AWS CLI (`aws lambda update-function-code`) — browser upload proved unreliable
- EventBridge Scheduler `futbol-report-schedule`: cron in `America/New_York`, target = Lambda Invoke, auto-created execution role
- **First scheduled auto-run confirmed** at 7:10 AM ET on May 28 — full CloudWatch log shows trigger → Brave → all 4 models → Redis write → site updated. End-to-end serverless pipeline running on its own.

### Hard-won lessons from the migration (interview-worthy war stories)

- **Runtime/binary mismatch:** Lambda was defaulted to Python 3.14 but the code was bundled for 3.12 — the `pydantic_core` C extension (a `cpython-312` `.so`) couldn't load. Fix: set the Lambda runtime to match the build target.
- **Mac vs. Linux binaries:** `uv`'s `--only-binary` didn't reliably fetch Linux wheels for `pydantic-core`; switching to `python3 -m pip` with explicit `--platform manylinux2014_x86_64` did.
- **Optional dependency:** `python-dotenv` isn't bundled for Lambda (env vars come from AWS), so the import had to be wrapped in try/except.
- **Timeout tuning:** default 3s → the pipeline needs ~4 min (13 Brave calls + 4 sequential model calls). Set to 900s ceiling.
- **Browser upload unreliable:** the console zip upload silently didn't update the deployed code (SHA-256 unchanged). AWS CLI upload was the reliable path.
- **Secrets discipline:** API keys leaked twice during the migration by pasting command output and console screenshots — rotated each time. The CI secret-scanner being added today is the systematic fix.

### Futbol Report — Redis index hygiene + TTLs (May 28)

- Switched eviction policy to `volatile-lru` and added a 90-day TTL on `run:*` keys via `ex=7776000`. `votes:*` and `runs:index` have no TTL, so they're protected from eviction — only old report data can ever be evicted.
- `MAX_RUNS_IN_INDEX = 50` constant + `LTRIM` after every push to cap the index.
- `_prune_stale_index_entries` helper removes index entries whose `run:*` key is gone. Uses a pipelined `EXISTS` batch (one round-trip) instead of N sequential calls.

### Futbol Report — project writeup live (May 30–31)

The `/projects/futbol-report` page is no longer just a grid — it has the full story:

- **Intro section** explaining what the comparison is and what the user is looking at, with a stated finding ("Claude tends to follow the format most closely, Gemma compresses hardest") followed by an invitation to disagree via the live voting.
- **"How it works" section** with a three-step pipeline description.
- **Architecture diagram** rendered as Tailwind-styled boxes (works in light + dark mode): EventBridge → Lambda → Brave + OpenRouter → Redis → Next.js.
- **Repo links** at the bottom — generator and site, both public.

### Harlie retired (May 31)

The old cron + tmux + Claude Code session on harlie is shut down. The cloud pipeline is the only running version. Telegram delivery is currently silent — see remaining work.

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
EventBridge Scheduler  (cron in America/New_York, every 3 days)
        │  invokes
        ▼
AWS Lambda  (futbol-report-generator, Python 3.12)
  main.handler → Brave Search + OpenRouter (4 LLMs) → writes run to Redis
        │
        ▼
   Redis (Vercel, volatile-lru, 30 MB)        ← shared handoff point
   - run:<timestamp>      = JSON {timestamp, generated_at, reports}   (TTL: 90 days)
   - runs:index           = list of timestamps, newest first, capped at 50
   - votes:<ts>:<model>   = integer counter
        │
        ▼
samiryuja.dev/  (Next.js on Vercel)
  /projects/futbol-report  → server-renders 2x2 grid + history + voting + writeup
  /api/vote                → records votes

(Telegram delivery: not yet implemented; planned as final Lambda step.)
(Local: `uv run main.py` still works for manual runs / testing.)
(Harlie: retired ✅.)
```

---

## Findings from Eval Runs

Real, observable, comparative findings — substance for the blog post and interview talking points.

1. **Brave search results are non-deterministic across runs.** Same query, ~30 min apart, different results. Live re-ranking. Implication: context must be consistent within a run (it is — one Brave call feeds all 4 models); thin results need graceful handling.
2. **Anti-hallucination clause held across all 4 model families.** "Use ONLY facts present in search results" generalized from Anthropic to Moonshot to Alibaba to Google. Prompt-level guardrails travel.
3. **Models differ sharply on context filtering.** An out-of-scope Indian Super League match was filtered out by Claude/Qwen/Gemma but surfaced by Kimi. Same prompt, same data, different prioritization.
4. **Information utilization varies with model size/family.** Claude and Kimi used the most context; Qwen middle; Gemma compressed hardest. A real cost/quality tradeoff.
5. **Format adherence ranking:** Claude > Qwen > Kimi > Gemma.
6. **Manager-change and transfer queries materially improved off-season output.** When fixtures dried up after Serie A ended, these queries kept reports substantive (Allegri sacking, Guardiola departure). "Let the data lead" handled the seasonal pivot with no calendar logic.

---

## Decisions Made

- **Telegram delivery: keep.** Will be added as the final step in the Lambda's `run_pipeline` — send the "best" report (Claude's by default; potentially the vote-winning one later) to the existing bot.
- **Redis eviction: `volatile-lru` with TTLs on reports.** Reports auto-expire after 90 days; votes and index are never evicted.
- **Single inference broker (OpenRouter), not direct provider SDKs.** Defensible architecture decision — the project's value is in the eval, not SDK plumbing.
- **No `main.py` module refactor.** Lambda works as one flat file. Not refactoring ahead of need.
- **Self-hosted blog on samiryuja.dev, not Medium/dev.to as primary.** Canonical URL stays on the portfolio.

---

## Known Issues / Future Improvements (Backlog)

### Model upgrade cadence

Review the `MODELS` constant in `main.py` once a quarter. Frontier model versions ship every few months; pinned slugs go stale. When bumping a slug (e.g. Claude Sonnet 4.5 → 4.6), do it as one deliberate commit with a clear message — that commit becomes the marker separating "old generation" runs from "new generation" runs in the history dropdown. Document major bumps in this tracker so the comparison's reproducibility story stays intact.

### Service credit top-ups

Brave, OpenRouter, and Vercel Redis are pay-as-you-go. Set a recurring calendar reminder (~monthly) to check balances and top up if low:

- OpenRouter: openrouter.ai/settings/credits
- Brave: Brave Search dashboard
- Vercel: Storage tab → Redis store → usage

### Voting integrity (today)

Currently per-page-load only — refresh re-enables voting. Use `localStorage` to enforce one vote per browser per run.

### Cosmetic polish

- **Report cell sizing/layout** — reports are different lengths so the grid reads as a tall 2-column stack. Cap cell height with internal scroll, or tabs. Not urgent.
- **Projects page placeholder** — "/projects" still says "Showcase your projects with a hero image (16 x 9)." One-line edit in `app/projects/page.tsx`. Quick.

### Optimizations (not needed at current scale)

- **`getVotes` uses `KEYS`** — scans the whole keyspace. Fine at current scale.
- **Page revalidation (ISR)** — comparison page is `force-dynamic`. ISR would cut Redis reads. Optimization only.
- **Slow Lambda runtime (~4 min)** — sequential Brave + sequential model calls. Could be parallelized. Not urgent at this cadence.
- **Thin-search-run handling** — fetch full page content for top results (Firecrawl/readability) when Brave snippets are sparse.

### Safety / hygiene

- **One-time git history secret scan** on both repos before broader publicity. The CI scanner being added today protects future commits, but should also confirm history is clean.
- **Secrets Manager (vs. env vars)** — current env vars are accepted at this scale. The hardening tier is AWS Secrets Manager (encrypted, rotatable, audited). The "how would you harden it?" answer.

### Hydration warning (in flight)

A "Recoverable Error" hydration mismatch showed up after the page writeup went in. The diff references Headless UI's portal markup — likely the template's search modal interacting with a browser extension, not our code. Confirm in incognito; if clean there, ignore.

---

## Parked Ideas (deliberately NOT doing)

Captured so they stop nagging. These are the tool-swap / scope-expansion pattern — revisit only with a concrete, job-search-relevant reason.

- **Build my own inference router (replace OpenRouter):** No. OpenRouter works. Weeks of work, no job-search payoff. The interesting story is the eval, not the plumbing.
- **vast.ai serverless / different compute layer:** No. Lambda is working. Don't swap the compute layer.
- **Custom email address (deferred twice during setup, then done):** Already handled with a redirecting custom email.

---

## What Remains — Today's Wrap-Up

In priority order. The goal is to close Project 0 cleanly so the next session opens on Project 1 (Hospitable / Airbnb).

1. **Blog post** — "Building a serverless multi-model report engine with live voting eval." Published on samiryuja.dev/blog. Highest leverage: it's the thing that makes the project discoverable beyond people who happen to land on the site. Distribute after: HN Show, LinkedIn, dev.to cross-post with canonical link.
2. **CI security scanning on both repos** — GitHub Actions workflow with gitleaks (secrets) + osv-scanner (dependency CVEs). Real, scoped, and a defensible resume bullet ("added secret scanning and OSV dependency checks to CI on every push").
3. **Telegram delivery from Lambda** — add a Telegram send step at the end of `run_pipeline`, reusing the harlie bot token. Bot resumes posting.
4. **Vote deduplication** — `localStorage`-based one-vote-per-browser-per-run guard in `VoteButton.tsx`.
5. **Projects-page placeholder copy swap** — one-line edit. 30 seconds.

## What Remains — After Today (Project 1)

- **Hospitable Agent Phase 1** (per the strategy doc).
- **Airbnb coverage problem** (per the strategy doc).
- Project 0 backlog items above can be picked up opportunistically but should not delay Project 1.

---

## Resume Material

### Truthfully claimable today

- Deployed a Next.js + Vercel portfolio with custom domain, automated CI/CD, and SSL
- Built and deployed an **event-driven serverless system on AWS** (Lambda + EventBridge Scheduler) that runs a scheduled multi-model LLM evaluation pipeline, integrating Brave Search and four frontier models (Anthropic Claude, Moonshot Kimi K2.6, Alibaba Qwen, Google Gemma) via OpenRouter, persisting results to Redis with TTL-based eviction and an explicit index hygiene policy, and rendering them on a public site with run history and visitor voting
- Diagnosed and resolved real serverless deployment issues: Python runtime/native-binary mismatches, Linux wheel packaging for `pydantic-core`, optional-dependency handling, Lambda timeout tuning, and an unreliable browser upload path resolved via the AWS CLI
- Surfaced measurable differences across model families in format adherence, context filtering, and information density on a repeated task; identified upstream search-API non-determinism and designed around it
- Made and can defend concrete architecture decisions: server-rendered vs. client-fetched pages, key-value vs. object storage, inference broker vs. direct provider SDKs, env vars vs. Secrets Manager, eviction policy (`volatile-lru`) chosen to protect votes/index while allowing report eviction

### Claimable once today's wrap-up items ship

- Configured CI security scanning (secret detection via gitleaks, dependency vulnerability scanning via OSV) on both project repos
- Implemented per-browser vote deduplication using browser storage
- Wrote and published a technical blog post on the system, including the multi-model eval methodology and AWS deployment debugging

### What to NOT say

- Do not undersell this. "I just call APIs" is the inversion of "I built and shipped a live, scheduled, serverless multi-model eval framework end to end — ingestion, multi-provider inference, persistence with explicit retention policy, a public web UI with voting, running automatically on AWS, with secret scanning in CI — and debugged the real deployment failures along the way."

---

## When You Sit Back Down

If you're closing Project 0 *today*: blog post first (highest leverage), then CI scanning (real and scoped), then Telegram (small), then vote dedup (small), then the projects-page copy swap (trivial). Do them in that order; if the day runs short, the blog post is the one that matters most for the job search.

If you're starting fresh after today: Project 1. Re-open the strategy doc and start on Hospitable Agent Phase 1. Project 0's backlog items can be picked up opportunistically — don't let them delay the new project.

---

## Anti-Distraction Reminders

From the strategy doc, Section 13:

1. One project at a time, shipped with public artifacts, beats eleven unfinished ones.
2. The AI familiarity gap is real but temporary — closes with project work, not study.
3. Underselling specific resume bullets and skills will cost interviews more than any missing technical skill.

Patterns observed across these sessions:

- Tool-swap research (Tavily, Cloudflare, templates, Brave, smaller Kimi models, "build my own router", vast.ai) is avoidance in disguise. Decide, move. The Parked Ideas section exists to hold these so they stop pulling focus.
- Scope expansion mid-build ("set up email", "World Cup pivot now") is the same pattern.
- Tidying/refactoring right after a milestone instead of pushing forward is a subtler version. Caught and acknowledged a few times across sessions — the awareness is the skill.
- Across these sessions you shipped a complete, live, automated, multi-part system — and pushed through some genuinely frustrating deployment slogs. That persistence is the thing that matters. Today is the last lap of Project 0; finish it, then move on.
