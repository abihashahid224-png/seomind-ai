import json
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()  # reads GEMINI_API_KEY from .env
MODELS = ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "gemini-3.8-flash"]
SKILLS_DIR = Path(__file__).parent / "skills"

AGENTS = {
    "keywords": "keyword-research",
    "title_meta": "title-meta",
    "content": "content-analysis",
    "headings": "heading-optimization",
    "linking": "internal-linking",
    "rewrite": "rewrite",
}


def load_skill(skill_name):
    text = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    return text.strip()


def call_gemma(prompt):
    last_error = None
    for model in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                return response.text or ""
            except Exception as e:
                last_error = e
                time.sleep(3)
    raise last_error


def parse_json(text):
    clean = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"raw": text}


def run_agent(agent_name, content, previous_results=""):
    prompt = (
        f"{load_skill(AGENTS[agent_name])}\n\n"
        f"# Blog content\n{content}\n\n"
        f"# Previous agents output\n{previous_results or 'none'}\n\n"
        "Return only valid JSON, no extra text."
    )
    return parse_json(call_gemma(prompt))