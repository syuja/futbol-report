# Job Search Progress Tracker

> Last updated: May 20, 2026
> Maintained as a working doc — update at the end of each session.

---

## Status Summary

| Milestone | Status |
|---|---|
| Personal site live with custom domain | ✅ Done |
| Soccer bot mapped & documented | ✅ Done |
| Futbol-report repo + Python prototype running | ✅ Done |
| Multi-model comparison (Project 0 core feature) | 🔄 In progress |
| Project page on personal site | ⏳ Not started |
| Blog post: "Building a serverless multi-model report engine" | ⏳ Not started |
| Hospitable Agent Phase 1 | ⏳ Not started |
| Airbnb coverage problem | ⏳ Not started |

---

## What Got Done (May 20, 2026)

### Personal Site — `samiryuja.dev`

- Domain registered (`samiryuja.dev`, $12.98/yr)
- GitHub repo: `syuja/samiryuja.dev`
- Forked `tailwind-nextjs-starter-blog` template
- Updated `siteMetadata.js`: name, title, description, GitHub, LinkedIn
- Deployed to Vercel with auto-deploy from `main`
- Custom domain + SSL configured
- Cleared example blog posts under `data/blog/`
- Site live at https://samiryuja.dev ✅

### Futbol Report (Project 0)

- Mapped existing harlie setup:
  - Cron triggers `soccer.sh` every 3 days
  - Script sends `soccer` into tmux session running Claude Code
  - Claude has a skill in `~/.claude/projects/-home-samir/memory/feedback_soccer_command.md`
  - Sends Telegram message via MCP tool (chat ID `8795167083`, token in `~/.claude/channels/telegram.json`)
  - **Old system still running on harlie — do not touch until replacement ships**
- Created GitHub repo: `futbol-report`
- Set up Python project with `uv` (Python 3.12)
- Dependencies: `openai`, `requests`, `python-dotenv`
- API keys obtained (stored in `.env`, gitignored):
  - Brave Search API (free tier)
  - OpenRouter ($5 credit added)
- Ported skill markdown to `prompts/futbol_skill.md`
- Wrote `main.py`: Brave searches → OpenRouter (Claude Sonnet 4.5) → save report
- Added paired logging: `logs/brave_<timestamp>.json` + `logs/reports/<model>_<timestamp>.md`
- First successful end-to-end run

---

## Known Issues

### Hallucination problem (Futbol Report)

The first run produced a report with mostly invented data:

- Fictional fixtures (e.g., "Roma vs Manchester United", "Real Madrid vs Bayern Munich")
- Invented standings ("Inter sits 4th with 68 points" — contradicts known reality)
- The Gimenez injury line was lifted verbatim from the **example in the prompt itself** — clear signal the model is filling context gaps from its own instructions

**Root cause:** Brave queries were too generic ("Serie A fixtures this week"), returning landing pages rather than specific data. Model + thin context = hallucination.

**Three fixes queued (start here next session):**

1. Tighten queries with explicit dates + add `freshness=pw` (past week) to Brave call. Bump `count` from 5 to 10.
2. Add anti-hallucination clause to the top of `futbol_skill.md`: "Use ONLY facts present in the provided search results. If data is missing, say so explicitly."
3. Remove or genericize the Gimenez example from the skill prompt so the model can't lift it verbatim.

### Quality gap vs. old tmux Claude version

Old tmux version produced higher-quality reports because Claude Code's native `WebSearch` tool returns richer context than Brave snippets. Two paths to close this gap:

- (A) Try Brave's **LLM Context API** endpoint (newer, returns pre-chunked ranked content for LLMs)
- (B) Add a second search pass that fetches full article content for top results (Firecrawl, or `requests` + readability)

Start with the cheap fix (the three above) before reaching for these.

---

## What Remains (Project 0)

In priority order:

1. **Fix hallucination** (3 fixes above) — should be 30 min
2. **Add more models** via OpenRouter — Claude Sonnet 4.5, GPT-5, Gemini 2.5, an open-source model (Llama 3.3 70B or DeepSeek). Loop over a list of model slugs, save one report per model per run.
3. **Persistence layer.** Local JSON files are fine for now. When moving to Lambda, switch to S3 or DynamoDB.
4. **Comparison view on `samiryuja.dev`.** Next.js API route reads from storage, renders side-by-side comparison.
5. **Visitor voting.** Simple endpoint that records which report the visitor prefers. (This is the eval framework. This is the interview story.)
6. **Move to Lambda + EventBridge.** Cron in EventBridge, code in Lambda. Drop harlie cron once stable.
7. **Telegram delivery.** Reuse the bot token from harlie. Send the "winning" report (by votes, or just Sonnet's by default).
8. **Decommission harlie's tmux + cron** once new system has run cleanly for a week.
9. **Project page on `samiryuja.dev`** at `/projects/futbol-report`.
10. **Blog post:** "Building a serverless multi-model report engine with live voting eval."

---

## Resume Material

### Things that can be truthfully claimed today

- Deployed a Next.js + Vercel portfolio with custom domain, automated CI/CD, and SSL
- Migrating a personal automation from a fragile single-server tmux setup to a cloud-native pipeline integrating Brave Search API and OpenRouter for multi-provider LLM access

### Things that can be claimed once Project 0 ships

(Wording from your strategy doc — these are the targets to write toward)

- Built and deployed an event-driven serverless system (Lambda + EventBridge) generating multi-model LLM comparisons for sports content, delivered via Telegram and rendered live on a public site
- Designed a live eval framework comparing outputs from N frontier models on the same prompt, with visitor voting to surface real-world model preference signals

### Things to NOT say

- Do not call this "small" or "incomplete." It's a shipped multi-system pipeline.
- Do not undersell — "I just call APIs" is the inversion of "I integrated four LLM providers behind a unified inference layer with structured eval."

---

## When You Sit Back Down

Open this file. Read the **What Remains** section. Start at item 1 (hallucination fixes). Don't shop, don't redesign, don't add features ahead of order. Three small edits to `main.py` and `futbol_skill.md`, then rerun, then send the new outputs.

The next session goal is **a clean, accurate report from one model**, nothing more. Multi-model comes after.

---

## Anti-Distraction Reminders

From the strategy doc, Section 13:

1. One project at a time, shipped with public artifacts, beats eleven unfinished ones.
2. The AI familiarity gap is real but temporary — closes with project work, not study.
3. Underselling specific resume bullets and skills will cost interviews more than any missing technical skill.

Specific patterns observed today:

- Researching alternatives to a decided tool (Tavily vs. others, Cloudflare vs. Namecheap, template comparison) is the avoidance pattern in disguise. Decide, move.
- Adding scope mid-build ("let's set up email", "World Cup pivot", "what blogs do other devs use") is the same pattern. Park ideas, return to the current step.
- Today you broke through it multiple times and shipped real work. Keep doing that.
