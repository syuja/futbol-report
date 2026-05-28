import redis

import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not needed on Lambda — env vars are set directly

BRAVE_API_KEY = os.environ["BRAVE_API_KEY"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

# Directory this file lives in — so prompt file loads correctly
# regardless of the working directory (Lambda runs from elsewhere).
BASE_DIR = Path(__file__).parent


def build_search_queries() -> list[str]:
    """Build queries covering near-term fixtures across active competitions."""
    today = datetime.now(ZoneInfo("America/New_York")).date()
    week_end = today + timedelta(days=7)
    date_range = f"{today.strftime('%B %-d')} to {week_end.strftime('%B %-d %Y')}"
    month_year = today.strftime("%B %Y")

    return [
        f"Serie A fixtures {date_range} schedule kickoff times",
        f"Serie A current matchday fixtures all games Saturday Sunday {month_year}",
        f"Serie A standings {month_year} points relegation Champions League qualification",
        f"Serie A results past weekend {month_year}",
        f"Serie A transfer news rumors {month_year}",
        f"biggest football transfers confirmed {month_year}",
        f"Serie A manager sacked appointed coaching change {month_year}",
        f"football manager changes news {month_year}",
        f"Champions League fixtures {date_range}",
        f"Champions League final 2026 schedule preview",
        f"FIFA World Cup 2026 schedule fixtures United States Mexico Canada",
        f"World Cup 2026 group draw teams matches",
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


def gather_context() -> str:
    """Run all searches, return combined context string."""
    sections = []
    for query in build_search_queries():
        result = brave_search(query)
        sections.append(f"## Search: {query}\n{result}")
    return "\n\n".join(sections)


def load_system_prompt() -> str:
    return (BASE_DIR / "prompts" / "futbol_skill.md").read_text()


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


def save_run_to_redis(timestamp: str, reports: dict[str, str]) -> None:
    """Store one run's reports in Redis and update the run index."""
    r = redis.from_url(os.environ["REDIS_URL"])
    generated_at = datetime.now(ZoneInfo("America/New_York")).isoformat()

    run_data = {
        "timestamp": timestamp,
        "generated_at": generated_at,
        "reports": reports,
    }
    r.set(f"run:{timestamp}", json.dumps(run_data))
    r.lpush("runs:index", timestamp)
    print(f"Saved run {timestamp} to Redis")


def run_pipeline() -> str:
    """The actual work: search, generate, save. Returns the run timestamp."""
    timestamp = datetime.now(ZoneInfo("America/New_York")).strftime("%Y%m%d_%H%M%S")
    models = [
        "anthropic/claude-sonnet-4.5",
        "moonshotai/kimi-k2.6",
        "qwen/qwen3.6-flash",
        "google/gemma-4-31b-it",
    ]

    print("Gathering web context...")
    context = gather_context()
    system_prompt = load_system_prompt()

    reports = {}
    for model in models:
        print(f"Generating report with {model}...")
        try:
            report = generate_report(system_prompt, context, model)
            reports[model] = report
        except Exception as e:
            print(f"FAILED for {model}: {e}")
            continue

    if reports:
        save_run_to_redis(timestamp, reports)

    print(f"All done. Reports for timestamp {timestamp}")
    return timestamp


def handler(event, context):
    """Lambda entry point. EventBridge triggers this."""
    timestamp = run_pipeline()
    return {"statusCode": 200, "timestamp": timestamp}


def main():
    """Local entry point — for `uv run main.py` on your laptop."""
    run_pipeline()


if __name__ == "__main__":
    main()