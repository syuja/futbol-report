**CRITICAL: Use ONLY facts present in the provided search results.**

- Do NOT invent fixtures, match times, scores, standings, or player injuries.
- If search results don't contain matches for a given day, write "No fixtures found in search results for this date."
- If a section can't be supported by the search results, omit it rather than filling with placeholders.
- The examples below show FORMAT only — do not copy their content into the output.

---

name: /soccer command trigger
description: When user says /soccer, generate a 7-day soccer schedule and send it via Telegram in a specific compact format
type: feedback
---

When the user says "/soccer", generate a soccer schedule for the next 7 days and send it via Telegram.

**What to include (in priority order):**

1. Whatever major competitions are active this week — the search results will tell you.
   Current candidates to watch for: Serie A, Champions League knockouts/final,
   FIFA World Cup 2026 (group stage starts June 11, 2026), domestic cup finals,
   Italy national team matches, summer transfer window news.
2. Within those, prioritize: title races, top-4 races, relegation battles,
   knockout-round fixtures, derbies, marquee matchups.
3. If a normally-prioritized competition (e.g., Serie A) has wrapped for the
   season, do not list its matches. Pivot to whatever is active.
4. Always include 3-5 KEY UPDATES at the end — these can be results, transfers,
   injuries, qualifying news, or storylines, depending on what's happening.

**Format rules:**

1. Timestamp at the top: "🕒 Generated: [day, time in ET]"
2. "Next Match" section at the very top (only if within 24h):
   ⏭  Next: Team A vs Team B — [time ET] (in Xh Xm)
3. Compact layout — no extra blank lines, group matches tightly under each day
4. 🔥 MUST WATCH marked inline on the match line (not separated)
5. Notes always inline in parentheses, e.g. (Top 4 battle)
6. Prioritize mobile readability — clean, easy to skim
7. Key Soccer Updates at the end:
   - 3-5 detailed bullets (don't shorten too much)
   - Always include impacted team at the END in parentheses
   - Example format: "<Player Name> out with <injury> (<Team>)"

**Why:** User wants a quick-reference soccer digest on demand, optimized for mobile Telegram reading.

**How to apply:** Use WebSearch (always without asking permission) to find current fixtures, compile the digest, and send via Telegram reply.
