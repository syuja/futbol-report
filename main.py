import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BRAVE_API_KEY = os.environ["BRAVE_API_KEY"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

def build_search_queries() -> list[str]:
    """Build queries covering near-term fixtures across active competitions."""
    today = datetime.now(ZoneInfo("America/New_York")).date()
    week_end = today + timedelta(days=7)
    date_range = f"{today.strftime('%B %-d')} to {week_end.strftime('%B %-d %Y')}"
    month_year = today.strftime("%B %Y")

    return [
        # Serie A: dated + matchday-based (catches different content formats)
        f"Serie A fixtures {date_range} schedule kickoff times",
        f"Serie A current matchday fixtures all games Saturday Sunday {month_year}",
        f"Serie A standings {month_year} points relegation Champions League qualification",
        f"Serie A results past weekend {month_year}",

        # Champions League — covers semis, final, and post-season news
        f"Champions League fixtures {date_range}",
        f"Champions League final 2026 schedule preview",

        # World Cup 2026 — kicks off June 11
        f"FIFA World Cup 2026 schedule fixtures United States Mexico Canada",
        f"World Cup 2026 group draw teams matches",

        # Generic catch-all for whatever's hot
        f"biggest soccer matches this week {date_range}",
    ]

def brave_search(query: str, count: int = 10) -> str:
    """Call Brave Search API, return concatenated snippets."""
    resp = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": BRAVE_API_KEY, "Accept": "application/json"},
        params={"q": query, "count": count, "freshness": "pw"},
        timeout=15,
    )
    resp.raise_for_status()
    results = resp.json().get("web", {}).get("results", [])
    return "\n".join(
        f"- {r.get('title', '')}: {r.get('description', '')}" for r in results
    )

def gather_context(timestamp: str) -> str:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"brave_{timestamp}.json"
    sections = []
    raw_results = {}
    for query in build_search_queries():
        result = brave_search(query)
        raw_results[query] = result
        sections.append(f"## Search: {query}\n{result}")

    log_file.write_text(json.dumps(raw_results, indent=2))
    print(f"Logged Brave results to {log_file}")
    return "\n\n".join(sections)

def load_system_prompt() -> str:
    return Path("prompts/futbol_skill.md").read_text()


def generate_report(system_prompt: str, context: str, model: str) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    now_et = datetime.now(ZoneInfo("America/New_York")).strftime("%A, %b %d at %-I:%M %p ET")
    user_message = (
        f"Current time: {now_et}\n\n"
        f"Web search results:\n\n{context}\n\n"
        f"Generate the soccer digest now."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content

def save_report(report: str, model_slug: str, timestamp: str) -> Path:
    reports_dir = Path("logs/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    safe_model = model_slug.replace("/", "_").replace(".", "_")
    report_file = reports_dir / f"{safe_model}_{timestamp}.md"
    report_file.write_text(report)
    return report_file

def main():
    timestamp = datetime.now(ZoneInfo("America/New_York")).strftime("%Y%m%d_%H%M%S")
    models = [
        "anthropic/claude-sonnet-4.5",
        "moonshotai/kimi-k2.6",
        "qwen/qwen3.6-flash",
        "google/gemma-4-31b-it",
    ]

    print("Gathering web context...")
    context = gather_context(timestamp)
    system_prompt = load_system_prompt()

    for model in models:
        print(f"\nGenerating report with {model}...")
        try:
            report = generate_report(system_prompt, context, model)
            report_path = save_report(report, model, timestamp)
            print(f"Report saved to {report_path}")
        except Exception as e:
            print(f"FAILED for {model}: {e}")
            continue

    print(f"\nAll done. Reports for timestamp {timestamp}")

if __name__ == "__main__":
    main()
