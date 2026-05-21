# Job Search Progress Tracker

> Last updated: May 21, 2026 (~12:45 AM ET)
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
| Comparison view on `samiryuja.dev` | ⏳ Not started |
| Visitor voting endpoint | ⏳ Not started |
| Migration to Lambda + EventBridge | ⏳ Not started |
| Telegram delivery from new system | ⏳ Not started |
| Project page on personal site | ⏳ Not started |
| Blog post writeup | ⏳ Not started |
| Hospitable Agent Phase 1 | ⏳ Not started |
| Airbnb coverage problem | ⏳ Not started |

---

## What Got Done (May 20–21, 2026)

### Personal Site — `samiryuja.dev`

- Domain registered, GitHub repo, template forked, metadata updated
- Deployed to Vercel with custom domain + SSL
- Cleared template example content
- Site live at https://samiryuja.dev ✅

### Futbol Report (Project 0)

- Mapped existing harlie setup (cron → tmux → Claude Code → skill → Telegram MCP)
  - Old system still running — do NOT touch until replacement ships
- Created `futbol-report` repo with `uv` (Python 3.12)
- Dependencies: `openai`, `requests`, `python-dotenv`
- API keys in `.env` (gitignored): Brave Search, OpenRouter ($5 credit)
- Ported skill markdown to `prompts/futbol_skill.md`
- Built `main.py`:
  - Brave Search with `freshness=pw`, dated queries, broadened competition coverage (Serie A, Champions League, World Cup, generic "biggest matches")
  - Anti-hallucination clause in prompt
  - Genericized example text (Gimenez line) so models can't lift it verbatim
  - Multi-model loop over 4 model slugs via OpenRouter
  - Paired logging by timestamp (`logs/brave_<ts>.json` + `logs/reports/<model>_<ts>.md`)
- First multi-model run completed cleanly with all 4 models returning reports

### Models in current lineup

| Model | Slug | Notes |
|---|---|---|
| Claude Sonnet 4.5 | `anthropic/claude-sonnet-4.5` | Baseline |
| Kimi K2.6 | `moonshotai/kimi-k2.6` | Chinese open-weight MoE (1T total / 32B active) |
| Qwen 3.6 Flash | `qwen/qwen3.6-flash` | Small, fast, cheap; different lab |
| Gemma 4 31B IT | `google/gemma-4-31b-it` | Google open-weight, dense; cheapest |

---

## Findings from First Eval Run (May 21, 12:28 AM ET)

These are real, observable, comparative findings. They are the substance of the future blog post and the interview talking points.

### Finding 1: Brave search results are non-deterministic across runs

The same dated query produced meaningfully different result sets between two runs ~30 min apart. The earlier run surfaced a Yardbarker article with specific Round 38 fixtures; the second run didn't. This isn't a bug — search engines re-rank live — but it has real implications:

- **For the eval framework:** context must be cached per timestamp so the 4 models genuinely see identical inputs. Currently they do (one Brave call feeds all 4 models within a run), but rerunning the same prompt later won't reproduce the result.
- **For production reliability:** the system needs to gracefully handle thin search results rather than panic when fixtures aren't in the top-N.

### Finding 2: Anti-hallucination clause held across all 4 model families

None of the four models invented fixtures, scores, or news. The "use ONLY facts present in search results" instruction at the top of the skill prompt survived from Anthropic to Moonshot to Alibaba to Google. This is a prompt-design win and a finding worth noting — prompt-level guardrails generalize.

### Finding 3: Models differ sharply on context filtering

The Brave results included one Indian Super League match (Inter Kashi vs East Bengal). The skill prompt's priority list is Serie A, Champions League, Italy national team, World Cup — ISL is not in scope.

- **Claude, Qwen, Gemma:** all filtered it out (correct).
- **Kimi:** led the report with it as the "Next Match" (incorrect filtering — too literal with available context).

This is the kind of difference a multi-model eval is designed to surface. Same prompt, same data, different prioritization.

### Finding 4: Information utilization varies dramatically with model size/family

Same input, very different output density:

- **Claude:** most context utilized — Inter scudetto, two relegations, CL final with venue, full top-4 math, all three World Cup openers with stadiums.
- **Kimi:** most context utilized in the bullet section, similar to Claude.
- **Qwen 3.6 Flash:** middle ground — 5 bullets, all real.
- **Gemma 4 31B:** most compressed — 5 short bullets, no day-by-day breakdown.

Cheap/small models compress aggressively. That's a tradeoff worth surfacing in the eventual comparison UI.

### Finding 5: Format adherence ranking (this run)

Claude > Qwen > Kimi > Gemma.

- **Claude** followed the full skill prompt structure: day-by-day breakdown, Key Updates section, attributions in parentheses, emojis, the works.
- **Qwen** kept day-by-day but trimmed emojis.
- **Kimi** kept day-by-day but used a "Next Match" header that wasn't in the prompt (interesting initiative, but format drift).
- **Gemma** collapsed the day-by-day into a single "No major fixtures found" line and dropped most format conventions.

---

## Known Issues / Things to Improve

### Need a way to handle thin search runs

When Brave returns weak context (like this run did), every model produces a sparse report. Two ways to address:

- (a) **Retry with broader queries** on thin returns
- (b) **Fetch full page content** for top results instead of relying on snippets (Firecrawl or `requests` + readability)

Option (b) is the right long-term fix. Snippets are inherently lossy.

### Cron on harlie still running

The old system fires every 3 days. Doesn't conflict with the prototype but should be turned off once the new system can take over Telegram delivery.

### No Telegram delivery yet

The new system writes reports to disk. Telegram delivery from this codebase is a TODO before harlie can be retired.

---

## What Remains (Project 0)

In priority order:

1. **Comparison view on `samiryuja.dev`.** Next.js API route reads from somewhere (S3, Vercel KV, or just committed JSON), renders side-by-side comparison.
2. **Visitor voting.** Simple endpoint that records which report a visitor prefers. This is the eval framework. This is the interview story.
3. **Persistence layer.** Local JSON is fine for now. When moving to cloud, S3 or DynamoDB.
4. **Move to Lambda + EventBridge.** Cron in EventBridge, code in Lambda. Drop harlie cron once stable.
5. **Telegram delivery from new system.** Reuse bot token from harlie. Pick the "winning" report (by votes, or just Claude's by default).
6. **Decommission harlie's tmux + cron** after new system has run cleanly for a week.
7. **Optional polish:** full page content fetching for richer Brave context (Firecrawl).
8. **Project page on `samiryuja.dev`** at `/projects/futbol-report`.
9. **Blog post:** "Building a serverless multi-model report engine with live voting eval."

---

## Resume Material

### Things that can be truthfully claimed today

- Deployed a Next.js + Vercel portfolio with custom domain, automated CI/CD, and SSL
- Built a multi-model LLM evaluation pipeline integrating Brave Search API and four frontier models (Anthropic Claude, Moonshot Kimi K2.6, Alibaba Qwen, Google Gemma) via OpenRouter, surfacing measurable differences in format adherence, context filtering, and information utilization on a repeated content-generation task
- Identified and characterized non-determinism in search-API result sets across temporally-adjacent runs and designed around it

### Things that can be claimed once Project 0 ships

- Built and deployed an event-driven serverless system (Lambda + EventBridge) generating multi-model LLM comparisons for sports content, delivered via Telegram and rendered live on a public site
- Designed a live eval framework comparing outputs from N frontier models on the same prompt, with visitor voting to surface real-world model preference signals

### What to NOT say

- Do not undersell this. "I just call APIs" is the inversion of "I integrated four LLM providers behind a unified inference layer with structured eval, characterized model behavior on a real task, and identified upstream non-determinism."

---

## When You Sit Back Down

Read the **Findings** section above first — those are the substantive observations the project is producing, and they're easy to forget if you don't write them down.

Then start at **What Remains** item 1: the comparison view on `samiryuja.dev`. This is where Project 0 becomes a public artifact instead of a local script. The right starting step is probably:

1. Decide on persistence (start simple: commit one timestamp's JSON + reports to the personal site repo, render statically). Cloud storage can come later.
2. Sketch the comparison page: header, four columns or stacked rows, vote buttons under each.
3. Build it with a single timestamp first. Multi-run history comes later.

---

## Anti-Distraction Reminders

From the strategy doc, Section 13:

1. One project at a time, shipped with public artifacts, beats eleven unfinished ones.
2. The AI familiarity gap is real but temporary — closes with project work, not study.
3. Underselling specific resume bullets and skills will cost interviews more than any missing technical skill.

Patterns observed across this session:

- Researching alternatives to a decided tool (Tavily, Cloudflare, templates, "what blogs do other devs use") is avoidance in disguise. Decide, move.
- Scope expansion mid-build ("set up email", "World Cup pivot now", "what about smaller Kimi models") is the same pattern.
- Today you broke through it most of the time and shipped real work. Keep doing that.

Sleep. Real progress today.
