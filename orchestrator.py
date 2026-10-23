import json
from agents import AGENTS, run_agent


def run_pipeline(content, selected=None):
    selected = selected or list(AGENTS)
    results = {}
    # Run agents in AGENTS order, so rewrite runs last
    for name in AGENTS:
        if name not in selected:
            continue
        context = json.dumps(results, ensure_ascii=False) if results else ""
        results[name] = run_agent(name, content, context)
    return results