# Job Search Progress Tracker

> Last updated: May 26, 2026 (~9:15 AM ET)
> Maintained as a working doc — update at the end of each session.

---

## Status Summary

| Milestone | Status |
|---|---|
| Personal site live with custom domain | ✅ Done |
| Soccer bot mapped & documented | ✅ Done |
| Futbol-report repo + Python prototype running | ✅ Done |
| Multi-model pipeline (4 models via OpenRouter) | ✅ Done |
| First real eval run with comparative findings | ✅ Done |
| Persistence layer (Redis on Vercel) | ✅ Done |
| Comparison view on `samiryuja.dev` | ✅ Done |
| Run history selector | ✅ Done |
| Visitor voting | ✅ Done |
| Project linked in site Projects list | ✅ Done |
| Migration to Lambda + EventBridge | ⏳ Not started |
| Telegram delivery from new system | ⏳ Not started |
| Project writeup page content | ⏳ Not started |
| Blog post writeup | ⏳ Not started |
| Hospitable Agent Phase 1 | ⏳ Not started |
| Airbnb coverage problem | ⏳ Not started |

---

## What Got Done

### Personal Site — `samiryuja.dev` (May 20)

- Domain registered, GitHub repo, template forked (`tailwind-nextjs-starter-blog`), metadata updated
- Deployed to Vercel with custom domain + SSL
- Cleared template example content
- Site live at https://samiryuja.dev ✅

### Futbol Report — generator (May 20–21)

- Mapped existing harlie setup (cron → tmux → Claude Code → skill → Telegram MCP)
  - Old system still running — do NOT touch until replacement ships
- Created `futbol-report` repo with `uv` (Python 3.12)
- Dependencies: `openai`, `requests`, `python-dotenv`, `redis`
- API keys in `.env` (gitignored): Brave Search, OpenRouter ($5 credit), Redis URL
- Ported skill markdown to `prompts/futbol_skill.md`; cleaned out dead Claude Code frontmatter
- Built `main.py`:
  - Brave Search with `freshness=pw`, dated queries, broadened competition coverage (Serie A, Champions League, World Cup, transfers, manager changes, generic "biggest matches")
  - Anti-hallucination clause in prompt
  - Genericized example text (Gimenez line) so models can't lift it verbatim
  - Multi-model loop over 4 model slugs via OpenRouter
  - Paired logging by timestamp (`logs/brave_<ts>.json` + `logs/reports/<model>_<ts>.md`)
  - Writes each run to Redis (`save_run_to_redis`): `run:<ts>` JSON + `runs:index` list

### Futbol Report — website (May 25–26)

- Provisioned Redis on Vercel (free 30 MB tier, named `futbol-reports`)
- `lib/redis.ts` — `withRedis` helper + `getLatestRun`, `getRun`, `getAllTimestamps`, `getVotes`, `recordVote`
- `app/projects/futbol-report/page.tsx` — server-rendered comparison page, 2x2 grid, reads `?run=` param
- `app/projects/futbol-report/RunSelector.tsx` — client dropdown to switch between runs (history)
- `app/api/vote/route.ts` — POST endpoint that records a vote
- `app/projects/futbol-report/VoteButton.tsx` — client vote button under each report
- Added `@/lib/*` path alias to `tsconfig.json`
- Linked the project in `data/projectsData.ts` — now reachable from the Projects tab
- All live at https://samiryuja.dev/projects/futbol-report ✅

### Models in current lineup

| Model | Slug | Notes |
|---|---|---|
| Claude Sonnet 4.5 | `anthropic/claude-sonnet-4.5` | Baseline |
| Kimi K2.6 | `moonshotai/kimi-k2.6` | Chinese open-weight MoE (1T total / 32B active) |
| Qwen 3.6 Flash | `qwen/qwen3.6-flash` | Small, fast, cheap; different lab |
| Gemma 4 31B IT | `google/gemma-4-31b-it` | Google open-weight, dense; cheapest |

---

## Architecture (current state)

```
futbol-report/  (Python, runs on laptop)
  main.py → Brave Search + OpenRouter (4 LLMs) → writes run to Redis
        │
        ▼
   Redis (Vercel, free tier)        ← shared handoff point
   - run:<timestamp>      = JSON {timestamp, generated_at, reports}
   - runs:index           = list of timestamps, newest first
   - votes:<ts>:<model>   = integer counter
        │
        ▼
samiryuja.dev/  (Next.js on Vercel)
  /projects/futbol-report  → server-renders the 2x2 comparison grid
  /api/vote                → records votes
```

---

## Findings from Eval Runs

These are real, observable, comparative findings — substance for the blog post and interview talking points.

### Finding 1: Brave search results are non-deterministic across runs

The same dated query produced meaningfully different result sets between runs ~30 min apart. Not a bug — search engines re-rank live — but it has real implications:

- **For the eval framework:** context must be consistent within a run so the 4 models see identical inputs. Currently they do (one Brave call feeds all 4 models). Rerunning the same prompt later won't reproduce the result.
- **For production reliability:** the system needs to handle thin search results gracefully.

### Finding 2: Anti-hallucination clause held across all 4 model families

None of the four models invented fixtures, scores, or news. The "use ONLY facts present in search results" instruction survived from Anthropic to Moonshot to Alibaba to Google. Prompt-level guardrails generalize across model families.

### Finding 3: Models differ sharply on context filtering

Brave results included an out-of-scope Indian Super League match. Claude, Qwen, and Gemma filtered it out; Kimi led its report with it. Same prompt, same data, different prioritization — exactly what a multi-model eval is designed to surface.

### Finding 4: Information utilization varies dramatically with model size/family

Same input, very different output density. Claude and Kimi utilized the most context; Qwen sat in the middle; Gemma (cheapest/smallest) compressed hardest — short bullets, minimal day-by-day. A real cost/quality tradeoff.

### Finding 5: Format adherence ranking

Claude > Qwen > Kimi > Gemma. Claude followed the full skill-prompt structure; Qwen trimmed emojis; Kimi added a "Next Match" header not in the prompt; Gemma dropped most format conventions.

### Finding 6: Manager-change and transfer queries materially improved off-season output

After Serie A's season ended, fixture queries returned little. Adding transfer-news and manager-change queries (plus a prompt line telling the model an empty fixture list is fine if updates are rich) kept reports substantive — e.g. correctly surfacing the Allegri sacking and Guardiola departure. The "let the data lead" approach handled the seasonal pivot with no calendar logic.

---

## Known Issues / Future Improvements

Captured so they aren't lost. None of these block progress — they're the backlog.

### Voting integrity (deduplication)
Current voting is per-page-load only: the button disables after one click, but a refresh lets the same person vote again. It's a rough signal, not a rigorous poll. A real fix needs cookies, localStorage, or fingerprinting to enforce one vote per visitor. Acceptable for v1; revisit if the eval data needs to be trustworthy.

### Report cell sizing / layout
The four reports are different lengths, so the 2x2 grid is really a 2-column stack. Options for later polish: cap cell height with internal scroll, or switch to a tabbed layout (click a model to view). Cosmetic only — not urgent.

### `main.py` refactor
`main.py` is currently one flat file doing search, generation, local saving, Redis writing, and orchestration. Fine at current size. When doing the Lambda migration, split into modules (e.g. `search.py`, `models.py`, `storage.py`, `main.py`) — the reorganization belongs *with* that migration, not before it. Do NOT refactor ahead of need.

### Thin search runs
When Brave returns weak context, every model produces a sparse report. Two fixes, both work with Brave (no provider swap needed):
- (a) Retry with broader queries on thin returns
- (b) Fetch full page content for top results instead of snippets (Firecrawl or `requests` + readability)
Option (b) is the better long-term fix — snippets are inherently lossy.

### `getVotes` uses Redis `KEYS`
`getVotes` uses the `KEYS` command, which scans the whole keyspace. Fine at current scale (a handful of runs). If this ever grew large, switch to a `SCAN`-based approach or store vote totals in a hash per run.

### Page revalidation
The comparison page is `force-dynamic` — reads Redis on every request. Works fine. A later optimization is scheduled revalidation (ISR) so it re-renders periodically instead of per-request. Optimization only; not needed now.

### Cron on harlie still running
The old system fires every 3 days. Doesn't conflict with the new pipeline but should be turned off once the new system handles Telegram delivery.

### No Telegram delivery yet
The new system writes to Redis and disk but does not send to Telegram. Required before harlie can be retired.

### Custom email address
Deferred twice during setup. Optional polish — set up a custom site email when convenient. Not on the critical path.

---

## What Remains (Project 0)

In priority order:

1. **Move to Lambda + EventBridge.** Cron in EventBridge, generator in Lambda. Refactor `main.py` into modules as part of this. Drop harlie cron once stable.
2. **Telegram delivery from new system.** Reuse bot token from harlie. Send the "winning" report (by votes, or Claude's by default).
3. **Decommission harlie's tmux + cron** after the new system has run cleanly for a week.
4. **Optional polish:** full page-content fetching for richer Brave context; vote deduplication; report cell sizing.
5. **Project writeup** on the `/projects/futbol-report` page — add an intro/explanation section above the comparison grid.
6. **Blog post:** "Building a serverless multi-model report engine with live voting eval."

---

## Resume Material

### Things that can be truthfully claimed today

- Deployed a Next.js + Vercel portfolio with custom domain, automated CI/CD, and SSL
- Built and shipped a live multi-model LLM evaluation tool: a Python pipeline integrating Brave Search and four frontier models (Anthropic Claude, Moonshot Kimi K2.6, Alibaba Qwen, Google Gemma) via OpenRouter, with results persisted to Redis and rendered as a public side-by-side comparison with run history and visitor voting
- Surfaced measurable differences across model families in format adherence, context filtering, and information density on a repeated content-generation task
- Identified and designed around non-determinism in search-API result sets across temporally-adjacent runs
- Made and can defend concrete architecture decisions: server-rendered vs. client-fetched pages, key-value vs. object storage, inference broker vs. direct provider SDKs

### Things that can be claimed once the Lambda migration ships

- Built and deployed an event-driven serverless system (Lambda + EventBridge) generating scheduled multi-model LLM comparisons, delivered via Telegram and rendered live on a public site

### What to NOT say

- Do not undersell this. "I just call APIs" is the inversion of "I built and shipped a live multi-model eval framework end to end — ingestion, multi-provider inference, persistence, a public web UI with voting — and characterized real model behavior differences."

---

## When You Sit Back Down

The comparison view is fully shipped and live — grid, history, voting. Project 0's public artifact exists.

The next milestone is the **Lambda + EventBridge migration** (What Remains item 1). This is the bigger remaining piece and the one that retires harlie. The `main.py` module refactor happens *as part of* that migration, not before.

Before starting that, a smaller, high-value option: write the **project intro section** on the `/projects/futbol-report` page (item 5). It's quick, it makes the live page self-explanatory to anyone who lands on it (recruiters), and it forces you to articulate the Findings — which is also blog-post raw material. Reasonable to do that first as a warm-up, then start the Lambda work.

---

## Anti-Distraction Reminders

From the strategy doc, Section 13:

1. One project at a time, shipped with public artifacts, beats eleven unfinished ones.
2. The AI familiarity gap is real but temporary — closes with project work, not study.
3. Underselling specific resume bullets and skills will cost interviews more than any missing technical skill.

Patterns observed across these sessions:

- Researching alternatives to a decided tool (Tavily, Cloudflare, templates, Brave, search providers, smaller Kimi models) is avoidance in disguise. Decide, move.
- Scope expansion mid-build ("set up email", "World Cup pivot now") is the same pattern.
- Tidying/refactoring right after a milestone, instead of pushing to the next feature, is a subtler version of it — feels productive, defers the harder work.
- Across these sessions you broke through it most of the time and shipped a complete, live, multi-part system. Keep doing that.
